from typing import Optional

from fastapi import APIRouter, Header, Form
from starlette.requests import Request
from starlette.responses import RedirectResponse

from fastapi_msal.core import OptStrList, OptStr, client_config
from fastapi_msal.models import AuthToken, BearerToken
from fastapi_msal.security import MSALAuthCodeHandler, MSALScheme


class MSALAuthorization:
    def __init__(
        self, return_to_path: str = "/", tags: OptStrList = None,
    ):

        self.handler = MSALAuthCodeHandler()
        if not tags:
            tags = ["authentication"]
        self.return_to_path = return_to_path
        self.router = APIRouter(prefix=client_config.path_prefix, tags=tags)
        self.router.add_api_route(
            name="login",
            path=client_config.login_path,
            endpoint=self.login,
            methods=["GET"],
            include_in_schema=client_config.show_in_docs,
        )

        self.router.add_api_route(
            name="get_token",
            path=client_config.token_path,
            endpoint=self.get_token,
            methods=["GET"],
            include_in_schema=client_config.show_in_docs,
        )

        self.router.add_api_route(
            name="post_token",
            path=client_config.token_path,
            endpoint=self.post_token,
            methods=["POST"],
            response_model=BearerToken,
            include_in_schema=client_config.show_in_docs,
        )
        self.router.add_api_route(
            client_config.logout_path,
            self.logout,
            methods=["GET"],
            include_in_schema=client_config.show_in_docs,
        )

    async def login(
        self, request: Request, redirect_uri: OptStr = None, state: OptStr = None
    ) -> RedirectResponse:
        if not redirect_uri:
            redirect_uri = request.url_for("get_token")
        return await self.handler.authorize_redirect(
            request=request, redirec_uri=redirect_uri, state=state
        )

    async def get_token(
        self, request: Request, code: str, state: Optional[str]
    ) -> RedirectResponse:
        await self.handler.authorize_access_token(
            request=request, code=code, state=state
        )
        return RedirectResponse(
            url=f"{self.return_to_path}", headers=dict(request.headers.items())
        )

    async def post_token(self, request: Request, code: str = Form(...)) -> BearerToken:
        token: AuthToken = await self.handler.authorize_access_token(
            request=request, code=code
        )
        return BearerToken(access_token=token.id_token)

    async def logout(
        self, request: Request, referer: OptStr = Header(None)
    ) -> RedirectResponse:
        callback_url = (
            referer if referer else str(self.return_to_path)
        )  # TODO: Needs to see if this generic enough...
        # TODO: Make sure we can call that --> oauth2_scheme.remove_account_from_cache()
        return self.handler.logout(session=request.session, callback_url=callback_url)

    def get_scheme(self) -> MSALScheme:
        return MSALScheme(handler=self.handler)
