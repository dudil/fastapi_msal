from typing import Optional

from fastapi import Request, HTTPException, status, Form
from fastapi.openapi.models import (
    OAuthFlows as OAuthFlowsModel,
    OAuthFlowAuthorizationCode,
)
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from msal import SerializableTokenCache
from pydantic import BaseModel

from fastapi_msal.clients import AsyncConfClient
from fastapi_msal.core import MSALPolicies, OptStrList, OptStr
from fastapi_msal.models import AuthToken, IDTokenClaims, LocalAccount


class AuthResponse(BaseModel):
    state: str
    code: str


class BarrierToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MSALAuthorizedForm:
    """
    Code is taken from fastapi/security/oauth2.py

    This is a dependency class, use it like:

        @app.post("/login")
        def login(form_data: MSALAuthRequestForm = Depends()):
            data = form_data.parse()
            print(data.code)
            if data.satate
                print(data.state)
            return data

    It creates the following Form request parameters in your endpoint:

    code:
    state:

    """

    def __init__(
        self,
        code: str = Form(...),
        state: Optional[str] = Form(None),
    ):
        self.code = code
        self.state = state


class MSALAuthCodeHandler(OAuth2):
    def __init__(
        self,
        client_id: str,
        client_credential: str,
        authorize_url: str,
        token_url: str,
        b2c_authority: str,
        scopes: OptStrList = None,
        policy: MSALPolicies = MSALPolicies.LOGIN,
        token_cache: Optional[SerializableTokenCache] = None,
        app_name: OptStr = None,
        app_version: OptStr = None,
    ):
        if not scopes:
            scopes = []
        flows = OAuthFlowsModel(
            authorizationCode=OAuthFlowAuthorizationCode(
                authorizationUrl=authorize_url, tokenUrl=token_url
            )
        )
        super().__init__(flows=flows)

        self.authority = f"{b2c_authority}/{policy}"
        self.scopes = scopes
        self.cca: AsyncConfClient = AsyncConfClient(
            client_id=client_id,
            client_credential=client_credential,
            authority=self.authority,
            scopes=scopes,
            token_cache=token_cache,
            app_name=app_name,
            app_version=app_version,
        )

    async def __call__(self, request: Request) -> Optional[IDTokenClaims]:
        http_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise http_exception

        try:
            token_claims: Optional[IDTokenClaims] = await self.cca.validate_id_token(
                id_token=param
            )
            return token_claims
        except RuntimeError as err:
            # maybe expired - try to refresh
            print(err)
            decoded: Optional[IDTokenClaims] = self.cca.decode_id_token(id_token=param)
            if decoded:
                auth_token: Optional[AuthToken] = await self._get_token_from_cache(
                    user_id=decoded.user_id
                )
                if auth_token and auth_token.id_token:
                    try:
                        token_claims = await self.cca.validate_id_token(
                            id_token=auth_token.id_token
                        )
                        return token_claims
                    except (RuntimeError, AttributeError) as err:
                        print(err)

        raise http_exception

    def logout_url(self, callback_url: str) -> str:
        logout_url = f"{self.authority}/oauth2/v2.0/logout?post_logout_redirect_uri={callback_url}"
        return logout_url

    async def _get_token_from_cache(
        self, user_id: OptStr = None
    ) -> Optional[AuthToken]:
        accounts: list[LocalAccount] = await self.cca.get_accounts()
        if accounts and accounts[0] and accounts[0].local_account_id == user_id:
            token: Optional[AuthToken] = await self.cca.acquire_token_silent(
                account=accounts[0]
            )
            return token
        return None
