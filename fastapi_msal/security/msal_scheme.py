from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.openapi.models import OAuth2 as OAuth2Model
from fastapi.openapi.models import OAuthFlowAuthorizationCode, SecuritySchemeType
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param

from fastapi_msal.models import AuthToken, IDTokenClaims

from .msal_auth_code_handler import MSALAuthCodeHandler


class MSALScheme(SecurityBase):
    def __init__(
        self,
        authorization_url: str,
        token_url: str,
        handler: MSALAuthCodeHandler,
        refresh_url: Optional[str] = None,
        scopes: Optional[dict[str, str]] = None,
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

    async def __call__(self, request: Request) -> IDTokenClaims:
        http_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        authorization: Optional[str] = request.headers.get("Authorization")
        scheme, token = get_authorization_scheme_param(authorization)
        token_claims: Optional[IDTokenClaims] = None
        if authorization and scheme.lower() != "bearer":
            token_claims = await self.handler.parse_id_token(request=request, token=token, validate=True)
        else:
            session_token: Optional[AuthToken] = await self.handler.get_token_from_session(request=request)
            if session_token:
                token_claims = session_token.id_token_claims

        if not token_claims:
            raise http_exception
        return token_claims
