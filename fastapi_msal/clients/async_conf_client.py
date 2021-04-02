import json
from typing import Optional, TypeVar, Callable, Any, List
from starlette.concurrency import run_in_threadpool
from msal import ConfidentialClientApplication, SerializableTokenCache  # type: ignore
from msal.oauth2cli import oidc  # type: ignore

from fastapi_msal.core import MSALClientConfig, OptStr, StrsDict, OptStrsDict
from fastapi_msal.models import (
    AuthCode,
    AuthToken,
    IDTokenClaims,
    LocalAccount,
    AuthResponse,
)

T = TypeVar("T")


class AsyncConfClient:
    def __init__(
        self,
        client_config: MSALClientConfig,
        cache: Optional[SerializableTokenCache] = None,
    ):
        self.client_config = client_config
        self._cca = ConfidentialClientApplication(
            client_id=client_config.client_id,
            client_credential=client_config.client_credential,
            authority=client_config.authority,
            app_name=client_config.app_name,
            app_version=client_config.app_version,
            token_cache=cache,
        )

    @staticmethod
    async def __execute_async__(func: Callable[..., T], **kwargs: Any) -> T:
        result: T = await run_in_threadpool(func, **kwargs)
        return result

    @staticmethod
    def decode_id_token(id_token: str) -> Optional[IDTokenClaims]:
        decoded: OptStrsDict = json.loads(oidc.decode_part(id_token.split(".")[1]))
        if decoded:
            return IDTokenClaims.parse_obj(decoded)
        return None

    async def validate_id_token(
        self, id_token: str, nonce: OptStr = None
    ) -> IDTokenClaims:
        token_claims: OptStrsDict = await self.__execute_async__(
            self._cca.client.decode_id_token, id_token=id_token, nonce=nonce
        )
        return IDTokenClaims.parse_obj(token_claims)

    async def get_application_token(
        self, claims_challenge: OptStrsDict = None
    ) -> AuthToken:
        token: StrsDict = await self.__execute_async__(
            self._cca.acquire_token_for_client,
            scopes=self.client_config.scopes,
            claims_challenge=claims_challenge,
        )
        return AuthToken.parse_obj_debug(to_parse=token)

    async def get_delegated_user_token(
        self, user_assertion: str, claims_challenge: OptStrsDict = None
    ) -> AuthToken:
        token: StrsDict = await self.__execute_async__(
            self._cca.acquire_token_on_behalf_of,
            user_assertion=user_assertion,
            scopes=self.client_config.scopes,
            claims_challenge=claims_challenge,
        )
        return AuthToken.parse_obj_debug(token)

    async def initiate_auth_flow(
        self,
        redirect_uri: OptStr = None,
        state: OptStr = None,
        prompt: OptStr = None,
        login_hint: OptStr = None,
        domain_hint: OptStr = None,
        claims_challenge: OptStr = None,
    ) -> AuthCode:
        auth_code: StrsDict = await self.__execute_async__(
            func=self._cca.initiate_auth_code_flow,
            scopes=self.client_config.scopes,
            redirect_uri=redirect_uri,
            state=state,
            prompt=prompt,
            login_hint=login_hint,
            domain_hint=domain_hint,
            claims_challenge=claims_challenge,
        )
        return AuthCode.parse_obj_debug(to_parse=auth_code)

    async def finalize_auth_flow(
        self, auth_code_flow: AuthCode, auth_response: AuthResponse
    ) -> AuthToken:
        auth_token: StrsDict = await self.__execute_async__(
            self._cca.acquire_token_by_auth_code_flow,
            auth_code_flow=auth_code_flow.dict(exclude_none=True),
            auth_response=auth_response.dict(exclude_none=True),
            scopes=self.client_config.scopes,
        )
        return AuthToken.parse_obj_debug(to_parse=auth_token)

    async def remove_account(self, account: LocalAccount) -> None:
        await self.__execute_async__(
            self._cca.remove_account, account=account.dict(exclude_none=True)
        )

    async def get_accounts(self, username: OptStr = None) -> List[LocalAccount]:
        accounts_objects: List[StrsDict] = await self.__execute_async__(
            self._cca.get_accounts, username=username
        )
        accounts: List[LocalAccount] = [
            LocalAccount.parse_obj_debug(to_parse=ao) for ao in accounts_objects
        ]
        return accounts

    async def acquire_token_silent(
        self,
        account: Optional[LocalAccount],
        authority: OptStr = None,
        force_refresh: Optional[bool] = False,
        claims_challenge: OptStrsDict = None,
    ) -> Optional[AuthToken]:
        token = await self.__execute_async__(
            self._cca.acquire_token_silent,
            scopes=self.client_config.scopes,
            account=(account.dict(exclude_none=True) if account else None),
            authority=authority,
            force_refresh=force_refresh,
            claims_challenge=claims_challenge,
        )
        if token:
            return AuthToken.parse_obj_debug(to_parse=token)
        return None
