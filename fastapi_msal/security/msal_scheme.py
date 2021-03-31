from typing import Optional

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer

from fastapi_msal.core import client_config
from fastapi_msal.models import IDTokenClaims
from .msal_auth_code_handler import MSALAuthCodeHandler

_scheme: OAuth2AuthorizationCodeBearer = OAuth2AuthorizationCodeBearer(
    authorizationUrl=client_config.login_path, tokenUrl=client_config.token_path
)


class MSALScheme:
    def __init__(self, handler: MSALAuthCodeHandler):
        self.handler = handler

    async def __call__(
        self, request: Request, token: str = Depends(_scheme)
    ) -> IDTokenClaims:
        http_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        token_claims: Optional[IDTokenClaims] = await self.handler.parse_id_token(
            token=token, validate=True
        )
        if not token_claims:
            raise http_exception
        return token_claims
