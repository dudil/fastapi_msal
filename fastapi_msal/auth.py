from typing import Optional

from fastapi import APIRouter, Request, HTTPException, status, Header, Form
from fastapi.responses import RedirectResponse
from msal import SerializableTokenCache

from fastapi_msal.core import MSALPolicies
from fastapi_msal.core import OptStrList, OptStr
from fastapi_msal.models import AuthCode, AuthResponse, AuthToken, IDTokenClaims
from fastapi_msal.security import BarrierToken
from fastapi_msal.security import MSALAuthCodeHandler


class MSALAuthorization:
    def __init__(
        self,
        client_id: str,
        client_credential: str,
        tenant: str,
        policy: MSALPolicies,
        scopes: OptStrList = None,
        path_prefix: str = "/auth",
        login_path: str = "/login",
        token_path: str = "/token",
        logout_path: str = "/logout",
        token_cache: Optional[SerializableTokenCache] = None,
        app_name: OptStr = None,
        app_version: OptStr = None,
        tags: OptStrList = None,
    ):

        self.msal_handler = MSALAuthCodeHandler(
            client_id=client_id,
            client_credential=client_credential,
            tenant=tenant,
            policy=policy,
            authorize_url=f"{path_prefix}{login_path}",
            token_url=f"{path_prefix}{token_path}",
            scopes=scopes,
            token_cache=token_cache,
            app_name=app_name,
            app_version=app_version,
        )
        if not tags:
            tags = ["authentication"]
        self.router = APIRouter(prefix=path_prefix, tags=tags)
        self.router.add_api_route(name="login", path=login_path, endpoint=self.login, methods=["GET"])
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
        return await self.msal_handler.__call__(request=request)

    async def login(
        self, request: Request, state: OptStr = None, redirect_uri: OptStr = None,
    ) -> RedirectResponse:
        if not redirect_uri:
            redirect_uri = request.url_for("get_token")
        auth_code: AuthCode = await self.msal_handler.cca.initiate_auth_flow(
            redirect_uri=redirect_uri, state=state
        )
        request.session["auth_code"] = auth_code.json(exclude_none=True)
        response = RedirectResponse(auth_code.auth_uri)
        return response

    async def authorized_flow(
        self, request: Request, code: str, state: OptStr = None
    ) -> BarrierToken:
        http_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Error"
        )
        auth_code: AuthCode = AuthCode.parse_raw(request.session["auth_code"])
        if not auth_code:
            raise http_exception
        if not state:
            state = auth_code.state
        auth_response = AuthResponse(code=code, state=state)
        auth_token: AuthToken = await self.msal_handler.cca.finalize_auth_flow(
            auth_code_flow=auth_code, auth_response=auth_response
        )
        if auth_token.error or not auth_token.id_token:
            raise http_exception
        request.session["auth_token"] = auth_token.json(exclude_none=True)
        return BarrierToken(access_token=auth_token.id_token)

    async def get_token(self, request: Request, code: str, state: str) -> BarrierToken:
        return await self.authorized_flow(request=request, code=code, state=state)

    async def post_token(self, request: Request, code: str = Form(...)) -> BarrierToken:
        return await self.authorized_flow(request=request, code=code)

    async def logout(
        self, request: Request, referer: OptStr = Header(None)
    ) -> RedirectResponse:
        request.session.clear()
        callback_url = referer if referer else str(request.url_for("get_root"))
        logout_url = self.msal_handler.logout_url(callback_url)
        # TODO: Make sure we can call that --> oauth2_scheme.remove_account_from_cache()
        response = RedirectResponse(logout_url)
        return response
