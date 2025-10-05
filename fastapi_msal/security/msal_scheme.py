from typing import Callable, Optional

from fastapi import HTTPException, Request, status
from fastapi.openapi.models import OAuth2 as OAuth2Model
from fastapi.openapi.models import OAuthFlowAuthorizationCode, SecuritySchemeType
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param

from fastapi_msal.models import AuthToken, IDTokenClaims, TokenStatus, UserInfo

from .msal_auth_code_handler import MSALAuthCodeHandler


def default_claims_processing(request: Request, token_claims: IDTokenClaims) -> None:
    """Retrieve user info from token claims and add that to request.state"""
    request.state.user = UserInfo(**dict(token_claims))


class MSALScheme(SecurityBase):
    def __init__(
        self,
        authorization_url: str,
        token_url: str,
        handler: MSALAuthCodeHandler,
        refresh_url: Optional[str] = None,
        scopes: Optional[dict[str, str]] = None,
        claims_processing: Optional[Callable[[Request, IDTokenClaims], None]] = None
    ):
        self.handler = handler
        if not scopes:
            scopes = {}
        self.scheme_name = self.__class__.__name__

        flows = OAuthFlowsModel(
            authorizationCode=OAuthFlowAuthorizationCode(
                authorizationUrl=authorization_url,
                tokenUrl=token_url,
                scopes=scopes,
                refreshUrl=refresh_url,
            )
        )
        # needs further investigation (type...)
        self.model = OAuth2Model(flows=flows, type=SecuritySchemeType.oauth2)
        self.claims_processing = claims_processing

    async def __call__(self, request: Request) -> IDTokenClaims:
        http_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

        # 1. retrieve token from header or session
        token_claims: Optional[IDTokenClaims] = None
        # 1.a. retrieve token from header
        authorization: Optional[str] = request.headers.get("Authorization")
        scheme, token = get_authorization_scheme_param(authorization)
        if authorization and scheme.lower() == "bearer":
            token_claims = await self.handler.parse_id_token(token=token)
        else:
            # 1.b. retrieve token from session
            session_token: Optional[AuthToken] = await self.handler.get_token_from_session(request=request)
            if session_token:
                token_claims = session_token.id_token_claims

        # 2. validate token
        if not token_claims:
            http_exception.detail = "No token found"
            raise http_exception
        token_status: TokenStatus = token_claims.validate_token(client_id=self.handler.client_config.client_id)
        if token_status != TokenStatus.VALID:
            http_exception.detail = token_status.value
            raise http_exception
        if self.claims_processing:
            self.claims_processing(request, token_claims)
        return token_claims
