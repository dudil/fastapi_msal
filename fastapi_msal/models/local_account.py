from __future__ import annotations

from fastapi_msal.core import OptStr
from .base_auth_model import BaseAuthModel


class LocalAccount(BaseAuthModel):
    local_account_id: OptStr = None
    home_account_id: OptStr = None
    environment: OptStr = None
    realm: OptStr = None
    username: OptStr = None
    authority_type: OptStr = None
