from typing import Optional

from fastapi import Request, HTTPException, status
from fastapi.openapi.models import (
    OAuthFlows as OAuthFlowsModel,
    OAuthFlowAuthorizationCode,
)
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from msal import SerializableTokenCache
from pydantic import BaseModel

from fastapi_msal.clients import AsyncConfClient
from fastapi_msal.core import MSALPolicies, OptStrList, OptStr, StrsDict
from fastapi_msal.models import AuthToken, IDTokenClaims, LocalAccount


class AuthResponse(BaseModel):
    state: str
    code: str


class BarrierToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

    def generate_header(self) -> StrsDict:
        return {"Authorization": f"{self.token_type} {self.access_token}"}


class MSALAuthCodeHandler(OAuth2):
    def __init__(
        self,
        client_id: str,
        client_credential: str,
        tenant: str,
        policy: MSALPolicies,
        authorize_url: str,
        token_url: str,
        scopes: OptStrList = None,
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
        self.policy = policy
        self.tenant = tenant
        self.authority = self.get_authority_url()
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

    def get_authority_url(self) -> str:
        authority_url: str = ""
        if MSALPolicies.AAD_SINGLE == self.policy:
            authority_url = f"https://login.microsoftonline.com/common/{self.tenant}"
        elif MSALPolicies.AAD_MULTI == self.policy:
            authority_url = "https://login.microsoftonline.com/common/"
        elif (
            MSALPolicies.B2C_LOGIN == self.policy
            or MSALPolicies.B2C_PROFILE == self.policy
        ):
            authority_url = f"https://{self.tenant}.b2clogin.com/{self.tenant}.onmicrosoft.com/{self.policy}"

        return authority_url
