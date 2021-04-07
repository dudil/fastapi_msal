from typing import Optional, TypeVar, Type
from pydantic import BaseModel, PrivateAttr
from fastapi_msal.core import OptStrsDict, StrsDict, SessionManager

AuthModel = TypeVar("AuthModel", bound="BaseAuthModel")


class BaseAuthModel(BaseModel):
    _recieved: OptStrsDict = PrivateAttr(None)

    @classmethod
    def parse_obj_debug(cls: Type[AuthModel], to_parse: StrsDict) -> AuthModel:
        debug_model: AuthModel = cls.parse_obj(obj=to_parse)
        debug_model.__setattr__("_recieved", to_parse)
        return debug_model

    async def save_to_session(self: AuthModel, session: SessionManager) -> None:
        session.save(self)

    @classmethod
    async def load_from_session(
        cls: Type[AuthModel], session: SessionManager
    ) -> Optional[AuthModel]:
        return session.load(model_cls=cls)
