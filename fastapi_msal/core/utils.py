from enum import Enum
from typing import Optional, List, Dict

OptStr = Optional[str]
StrList = List[str]
OptStrList = Optional[StrList]
StrsDict = Dict[str, str]
OptStrsDict = Optional[StrsDict]


class MSALPolicies(str, Enum):
    LOGIN = "B2C_1_LOGIN"
    RESET_PASSWORD = "B2C_1_RESET_PASSWORD"
    PROFILE = "B2C_1_PROFILE"
