from typing import Optional

from fastapi import APIRouter, Header, Form
from starlette.requests import Request
from starlette.responses import RedirectResponse

from fastapi_msal.core import OptStrList, OptStr
from fastapi_msal.models import AuthToken, IDTokenClaims, BarrierToken, MSALClientConfig
from fastapi_msal.security import MSALAuthCodeHandler


class MSALAuthorization:
    def __init__(
        self,
        client_config: MSALClientConfig,
        path_prefix: str = "",
        login_path: str = "/login",
        token_path: str = "/token",
        logout_path: str = "/logout",
        return_to_path: str = "/",
        tags: OptStrList = None,
    ):

        self.handler = MSALAuthCodeHandler(
            client_config=client_config,
            authorize_url=f"{path_prefix}{login_path}",
            token_url=f"{path_prefix}{token_path}",
        )
        if not tags:
            tags = ["authentication"]
        self.return_to_path = return_to_path
        self.router = APIRouter(prefix=path_prefix, tags=tags)
        self.router.add_api_route(
            name="login", path=login_path, endpoint=self.login, methods=["GET"]
        )

        self.router.add_api_route(
            name="get_token",
            path=token_path,
            endpoint=self.get_token,
            methods=["GET"],
            response_model=BarrierToken,
        )

        self.router.add_api_route(
            name="post_token",
            path=token_path,
            endpoint=self.post_token,
            methods=["POST"],
            response_model=BarrierToken,
        )
        self.router.add_api_route(f"/{logout_path}", self.logout, methods=["GET"])

    async def __call__(self, request: Request) -> Optional[IDTokenClaims]:
        return await self.handler.__call__(request=request)

    async def login(
        self, request: Request, redirec_uri: OptStr = None,
    ) -> RedirectResponse:
        if not redirec_uri:
            redirec_uri = request.url_for("get_token")
        return await self.handler.authorize_redirect(
            request=request, redirec_uri=redirec_uri
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

    async def post_token(self, request: Request, code: str = Form(...)) -> BarrierToken:
        token: AuthToken = await self.handler.authorize_access_token(
            request=request, code=code
        )
        return BarrierToken(token=token.id_token)

    async def logout(
        self, request: Request, referer: OptStr = Header(None)
    ) -> RedirectResponse:
        callback_url = (
            referer if referer else str(self.return_to_path)
        )  # TODO: Needs to see if this generic enough...
        # TODO: Make sure we can call that --> oauth2_scheme.remove_account_from_cache()
        return self.handler.logout(session=request.session, callback_url=callback_url)
