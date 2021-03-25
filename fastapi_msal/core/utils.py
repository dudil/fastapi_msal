from enum import Enum
from typing import Optional, List, Dict

OptStr = Optional[str]
StrList = List[str]
OptStrList = Optional[StrList]
StrsDict = Dict[str, str]
OptStrsDict = Optional[StrsDict]


class MSALPolicies(str, Enum):
    AAD_MULTI = "AAD_MULTI"
    AAD_SINGLE = "AAD_SINGLE"
    B2C_LOGIN = "B2C_1_LOGIN"
    B2C_PROFILE = "B2C_1_PROFILE"
