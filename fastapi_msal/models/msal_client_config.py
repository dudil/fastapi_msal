from typing import Optional
from enum import Enum
from pydantic import BaseSettings
from fastapi_msal.core import OptStr, StrList


class MSALPolicies(str, Enum):
    AAD_MULTI = "AAD_MULTI"
    AAD_SINGLE = "AAD_SINGLE"
    B2C_LOGIN = "B2C_1_LOGIN"
    B2C_PROFILE = "B2C_1_PROFILE"


class MSALClientConfig(BaseSettings):
    class Config:
        env_file = "fastapi_msal.env"

    client_id: OptStr
    client_credential: OptStr
    tenant: OptStr
    policy: Optional[MSALPolicies]
    scopes: StrList = list[str]()
    app_name: OptStr = None
    app_version: OptStr = None

    @property
    def authority(self) -> str:
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
