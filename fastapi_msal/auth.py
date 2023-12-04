from typing import Annotated, Optional

from fastapi import APIRouter, Form, Header
from starlette.requests import Request
from starlette.responses import RedirectResponse

from fastapi_msal.core import MSALClientConfig, OptStr
from fastapi_msal.models import AuthToken, BearerToken, IDTokenClaims
from fastapi_msal.security import MSALAuthCodeHandler, MSALScheme


class MSALAuthorization:
    def __init__(
        self,
        client_config: MSALClientConfig,
        return_to_path: str = "/",
        tags: Optional[list[str]] = None,  # type: ignore [unused-ignore]
    ):
        self.handler = MSALAuthCodeHandler(client_config=client_config)
        if not tags:
            tags = ["authentication"]
        self.return_to_path = return_to_path
        self.router = APIRouter(prefix=client_config.path_prefix, tags=tags)  # type: ignore
        self.router.add_api_route(
            name="_login_route",
            path=client_config.login_path,
            endpoint=self._login_route,
            methods=["GET"],
            include_in_schema=client_config.show_in_docs,
        )

        self.router.add_api_route(
            name="_get_token_route",
            path=client_config.token_path,
            endpoint=self._get_token_route,
            methods=["GET"],
            include_in_schema=client_config.show_in_docs,
        )

        self.router.add_api_route(
            name="_post_token_route",
            path=client_config.token_path,
            endpoint=self._post_token_route,
            methods=["POST"],
            response_model=BearerToken,
            include_in_schema=client_config.show_in_docs,
        )
        self.router.add_api_route(
            client_config.logout_path,
            self._logout_route,
            methods=["GET"],
            include_in_schema=client_config.show_in_docs,
        )

    async def _login_route(
        self,
        request: Request,
        redirect_uri: OptStr = None,
        state: OptStr = None,
        client_id: OptStr = None,
    ) -> RedirectResponse:
        if client_id:
            print(client_id)
        if not redirect_uri:
            redirect_uri = str(request.url_for("_get_token_route"))
        return await self.handler.authorize_redirect(request=request, redirec_uri=redirect_uri, state=state)

    async def _get_token_route(self, request: Request, code: str, state: OptStr) -> RedirectResponse:
        await self.handler.authorize_access_token(request=request, code=code, state=state)
        return RedirectResponse(url=f"{self.return_to_path}", headers=dict(request.headers.items()))

    async def _post_token_route(
        self, request: Request, code: Annotated[str, Form()], state: Annotated[OptStr, Form()] = None
    ) -> BearerToken:
        token: AuthToken = await self.handler.authorize_access_token(request=request, code=code, state=state)
        return BearerToken(access_token=token.id_token)

    async def _logout_route(
        self, request: Request, referer: Annotated[OptStr, Header()] = None, callback_url: OptStr = None
    ) -> RedirectResponse:
        # check if callback_url is set, if not try to get it from referer header
        callback_url = referer if referer else str(self.return_to_path)
        return self.handler.logout(request=request, callback_url=callback_url)

    async def get_session_token(self, request: Request) -> Optional[AuthToken]:
        return await self.handler.get_token_from_session(request=request)

    async def check_authenticated_session(self, request: Request) -> bool:
        auth_token: Optional[AuthToken] = await self.get_session_token(request)
        if auth_token:
            token_claims: Optional[IDTokenClaims] = await self.handler.parse_id_token(token=auth_token)
            if token_claims and token_claims.validate_token():
                return True
        return False

    @property
    def scheme(self) -> MSALScheme:
        return MSALScheme(
            authorization_url=self.router.url_path_for("_login_route"),
            token_url=self.router.url_path_for("_post_token_route"),
            handler=self.handler,
        )
