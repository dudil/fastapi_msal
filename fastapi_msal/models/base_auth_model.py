from __future__ import annotations
from typing import Optional, TypeVar, Type
from pydantic import BaseModel, PrivateAttr
from fastapi_msal.core import OptStrsDict, StrsDict, OptStr

AuthModel = TypeVar("AuthModel", bound="BaseAuthModel")


class BaseAuthModel(BaseModel):
    _recieved: OptStrsDict = PrivateAttr(None)

    @classmethod
    def parse_obj_debug(cls: Type[AuthModel], to_parse: StrsDict) -> AuthModel:
        debug_model: AuthModel = cls.parse_obj(obj=to_parse)
        debug_model.__setattr__("_recieved", to_parse)
        return debug_model

    def save_to_session(self: AuthModel, session: StrsDict) -> None:
        session.update({self.__repr_name__(): self.json(exclude_none=True)})

    @classmethod
    def load_from_session(
        cls: Type[AuthModel], session: StrsDict
    ) -> Optional[AuthModel]:
        raw_object: OptStr = session.get(cls.__name__, None)
        if raw_object:
            return cls.parse_raw(raw_object)
        return None
