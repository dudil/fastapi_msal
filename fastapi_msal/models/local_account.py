from __future__ import annotations
from pydantic import BaseModel, PrivateAttr

from fastapi_msal.core import OptStr, OptStrsDict, StrsDict


class LocalAccount(BaseModel):
    local_account_id: OptStr = None
    home_account_id: OptStr = None
    environment: OptStr = None
    realm: OptStr = None
    username: OptStr = None
    authority_type: OptStr = None

    _received: OptStrsDict = PrivateAttr(None)

    @classmethod
    def parse_dict(cls: LocalAccount, to_parse: StrsDict) -> LocalAccount:
        account: LocalAccount = cls.parse_obj(to_parse)
        account._received = to_parse
        return account
