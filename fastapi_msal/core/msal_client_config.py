from enum import Enum
from typing import ClassVar

from pydantic_settings import BaseSettings

from .utils import OptStr


class MSALPolicies(str, Enum):
    AAD_MULTI = "AAD_MULTI"
    AAD_SINGLE = "AAD_SINGLE"
    B2C_LOGIN = "B2C_1_LOGIN"
    B2C_PROFILE = "B2C_1_PROFILE"
    B2C_CUSTOM = "B2C_1A_LOGIN"


class MSALClientConfig(BaseSettings):
    # The following params must be set according to the app registration data recieved from AAD
    # https://docs.microsoft.com/azure/active-directory/develop/quickstart-v2-register-an-app
    client_id: OptStr = None
    client_credential: OptStr = None
    tenant: OptStr = None

    # Optional to set, see MSALPolicies for different options, default is single AAD (B2B)
    policy: MSALPolicies = MSALPolicies.AAD_SINGLE
    # Optional to set - If you are unsure don't set - it will be filled by MSAL as required
    scopes: ClassVar[list[str]] = []
    # Not in use - for future support
    session_type: str = "filesystem"

    # Set the following params if you wish to change the default MSAL Router endpoints
    path_prefix: str = ""
    login_path: str = "/_login_route"
    token_path: str = "/token"
    logout_path: str = "/_logout_route"
    show_in_docs: bool = False

    # Optional Params for Logging and Telemetry with AAD
    app_name: OptStr = None
    app_version: OptStr = None

    @property
    def authority(self) -> str:
        if not self.policy:
            msg = "Policy must be specificly set before use"
            raise ValueError(msg)
        authority_url: str = ""
        if MSALPolicies.AAD_SINGLE == self.policy:
            authority_url = f"https://login.microsoftonline.com/{self.tenant}"
        elif MSALPolicies.AAD_MULTI == self.policy:
            authority_url = "https://login.microsoftonline.com/common/"
        elif self.policy not in {
            MSALPolicies.AAD_SINGLE,
            MSALPolicies.AAD_MULTI,
            MSALPolicies.B2C_LOGIN,
            MSALPolicies.B2C_PROFILE,
            MSALPolicies.B2C_CUSTOM,
        }:
            authority_url = f"https://{self.tenant}.b2clogin.com/{self.tenant}.onmicrosoft.com/{self.policy}"

        return authority_url

    @property
    def login_full_path(self) -> str:
        return f"{self.path_prefix}{self.login_path}"
