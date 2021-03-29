from __future__ import annotations

from fastapi_msal.core import OptStr, OptStrList
from .base_auth_model import BaseAuthModel


class AuthCode(BaseAuthModel):
    state: str
    redirect_uri: str
    auth_uri: str
    scope: OptStrList = None
    code_verifier: OptStr = None
    claims_challenge: OptStr = None
    nonce: OptStr = None
