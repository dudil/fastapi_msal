from fastapi import APIRouter, Request, HTTPException, status, Header
from fastapi.responses import RedirectResponse

from fastapi_msal.core import OptStrList, OptStr
from fastapi_msal.models import AuthCode, AuthResponse, AuthToken
from fastapi_msal.security import MSALAuthCodeHandler, MSALAuthorizedForm
from fastapi_msal.security.msal_auth_code_handler import BarrierToken

"""
msal_handler = MSALAuthCodeHandler(
    b2c_authority=config.b2c_authority,
    client_id=config.auth_client_id,
    client_credential=config.auth_client_secret,

    authorize_url="/auth/login",
    token_url="/auth/authorized",
    scopes=config.auth_scope,
)"""


class MsalAuthorizationRouter:
    def __init__(
        self,
        msal_handler: MSALAuthCodeHandler,
        prefix: str = "/auth",
        tags: OptStrList = None,
    ):
        self.msal_handler = msal_handler
        if not tags:
            tags = ["authentication"]
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.router.add_api_route(
            "/login", self.login, methods=["GET"], response_model=RedirectResponse
        )
        self.router.add_api_route(
            "/token", self.get_token, methods=["GET"], response_model=BarrierToken
        )
        self.router.add_api_route(
            "/authorized",
            self.post_authorized,
            methods=["POST"],
            response_model=BarrierToken,
        )
        self.router.add_api_route("/logout", self.logout, methods=["GET"])

    async def login(
        self,
        request: Request,
        state: OptStr = None,
        redirect_uri: OptStr = None,
    ) -> RedirectResponse:
        if not redirect_uri:
            redirect_uri = request.url_for("token")
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

    async def post_authorized(
        self, request: Request, code: str = MSALAuthorizedForm(...)
    ) -> BarrierToken:
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


"""
@router.get("/me", response_model=UserInfo, response_model_by_alias=False)
async def get_me_info(token_claims: IDTokenClaims = Depends(oauth2_scheme)) -> UserInfo:
    return token_claims
"""