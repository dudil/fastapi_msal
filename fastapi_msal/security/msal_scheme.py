from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.openapi.models import OAuth2 as OAuth2Model
from fastapi.openapi.models import OAuthFlowAuthorizationCode, SecuritySchemeType
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param

from fastapi_msal.models import IDTokenClaims

from .msal_auth_code_handler import MSALAuthCodeHandler


class MSALScheme(SecurityBase):
    def __init__(
        self,
        authorization_url: str,
        token_url: str,
        handler: MSALAuthCodeHandler,
        refresh_url: Optional[str] = None,
        scopes: Optional[dict[str, str]] = None,
        accepted_roles: Optional[Union[str, list[str]]] = None,
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
        self.accepted_roles = accepted_roles

    async def __call__(self, request: Request) -> IDTokenClaims:
        http_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        authorization: Optional[str] = request.headers.get("Authorization")
        scheme, token = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise http_exception
        try:
            token_claims: Optional[IDTokenClaims] = await self.handler.parse_id_token(
                request=request, token=token, validate=True
            )
        except Exception as e:
            http_exception.detail = str(e)
            raise http_exception
        if not token_claims:
            raise http_exception

        # If accepted roles were indicated we ensure at least one is present
        if self.accepted_roles:
            accepted = self.accepted_roles
            if isinstance(accepted, str):
                accepted = [accepted]
            rbac_exec = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Not authorized - one of {','.join(accepted)} roles required",
                headers={"WWW-Authenticate": "Bearer"},
            )
            if roles := token_claims.roles:
                if not set(roles).intersection(accepted):
                    raise rbac_exec
            else:
                raise rbac_exec
        # else we don't perform rbac and accept the token
        return token_claims
