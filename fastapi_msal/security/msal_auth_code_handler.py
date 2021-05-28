from typing import Optional, Union

from msal import SerializableTokenCache  # type: ignore
from fastapi import Request, HTTPException, status

from starlette.responses import RedirectResponse

from fastapi_msal.clients import AsyncConfClient
from fastapi_msal.core import MSALClientConfig, OptStr, StrsDict, SessionManager
from fastapi_msal.models import (
    AuthToken,
    IDTokenClaims,
    LocalAccount,
    AuthCode,
    AuthResponse,
)


class MSALAuthCodeHandler:
    def __init__(self, client_config: MSALClientConfig):
        self.client_config: MSALClientConfig = client_config

    async def authorize_redirect(
        self, request: Request, redirec_uri: str, state: OptStr = None
    ) -> RedirectResponse:
        auth_code: AuthCode = await self.msal_app().initiate_auth_flow(
            redirect_uri=redirec_uri, state=state
        )
        session = SessionManager(request=request)
        session.init_session(session_id=auth_code.state)
        await auth_code.save_to_session(session=SessionManager(request=request))
        return RedirectResponse(auth_code.auth_uri)

    async def authorize_access_token(
        self, request: Request, code: str, state: OptStr = None
    ) -> AuthToken:
        http_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Error"
        )
        auth_code: Optional[AuthCode] = await AuthCode.load_from_session(
            session=SessionManager(request=request)
        )
        if (not auth_code) or (not auth_code.state):
            raise http_exception
        if state and (
            state != auth_code.state
        ):  # extra validation for correct state if passed in
            raise http_exception
        auth_response = AuthResponse(code=code, state=auth_code.state)
        cache: SerializableTokenCache = self._load_cache(session=request.session)
        auth_token: AuthToken = await self.msal_app(cache=cache).finalize_auth_flow(
            auth_code_flow=auth_code, auth_response=auth_response
        )
        if auth_token.error or not auth_token.id_token:
            raise http_exception
        await auth_token.save_to_session(session=SessionManager(request=request))
        self._save_cache(session=request.session, cache=cache)
        return auth_token

    # TODO: needs rewrite of method, probably seperate into 2 different methods
    async def parse_id_token(
        self, request: Request, token: Union[AuthToken, str], validate: bool = True
    ) -> Optional[IDTokenClaims]:
        if isinstance(token, AuthToken):
            id_token: str = token.id_token
        else:
            id_token = token
        auth_token: Optional[AuthToken] = await self.get_token_from_session(
            request=request
        )
        if (
            auth_token
            and auth_token.id_token == id_token
            and auth_token.id_token_claims
            and not validate
        ):
            return auth_token.id_token_claims
        if validate:
            return await self.msal_app().validate_id_token(id_token=id_token)
        return self.msal_app().decode_id_token(id_token=id_token)

    def logout(self, request: Request, callback_url: str) -> RedirectResponse:
        SessionManager(request=request).clear()
        logout_url = f"{self.client_config.authority}/oauth2/v2.0/logout?post_logout_redirect_uri={callback_url}"
        return RedirectResponse(url=logout_url)

    @staticmethod
    async def get_token_from_session(request: Request) -> Optional[AuthToken]:
        return await AuthToken.load_from_session(
            session=SessionManager(request=request)
        )

    @staticmethod
    def _load_cache(session: StrsDict) -> SerializableTokenCache:
        cache: SerializableTokenCache = SerializableTokenCache()
        token_cache = session.get("token_cache", None)
        if token_cache:
            cache.deserialize(token_cache)
        return cache

    @staticmethod
    def _save_cache(session: StrsDict, cache: SerializableTokenCache) -> None:
        if cache.has_state_changed:
            session["token_cache"] = cache.serialize()

    def msal_app(
        self, cache: Optional[SerializableTokenCache] = None
    ) -> AsyncConfClient:
        return AsyncConfClient(client_config=self.client_config, cache=cache)

    async def _get_token_from_cache(
        self, session: StrsDict, user_id: OptStr = None
    ) -> Optional[AuthToken]:
        cache: SerializableTokenCache = self._load_cache(session=session)
        acc: AsyncConfClient = self.msal_app(cache=cache)
        accounts: list[LocalAccount] = await acc.get_accounts()
        if accounts and accounts[0] and accounts[0].local_account_id == user_id:
            token: Optional[AuthToken] = await acc.acquire_token_silent(
                account=accounts[0]
            )
            self._save_cache(session=session, cache=cache)
            return token
        return None
