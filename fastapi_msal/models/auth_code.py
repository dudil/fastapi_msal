from __future__ import annotations
from pydantic import BaseModel, PrivateAttr

from fastapi_msal.core import OptStr, OptStrList, StrsDict, OptStrsDict


class AuthCode(BaseModel):
    state: str
    redirect_uri: str
    auth_uri: str
    scope: OptStrList = None
    code_verifier: OptStr = None
    claims_challenge: OptStr = None
    nonce: OptStr = None
    _received: OptStrsDict = PrivateAttr(None)

    @classmethod
    def parse_dict(cls: AuthCode, to_parse: StrsDict) -> AuthCode:
        auth_code: AuthCode = cls.parse_obj(to_parse)
        auth_code._received = to_parse
        return auth_code


class AuthResponse(BaseModel):
    state: OptStr = None
    code: OptStr = None
