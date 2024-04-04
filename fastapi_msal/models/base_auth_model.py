from typing import Optional, TypeVar

from pydantic import BaseModel, ConfigDict, PrivateAttr

from fastapi_msal.core import OptStrsDict, SessionManager, StrsDict

AuthModel = TypeVar("AuthModel", bound="BaseAuthModel")


class BaseAuthModel(BaseModel):
    _recieved: OptStrsDict = PrivateAttr(None)
    model_config = ConfigDict(extra="allow")
    """
    extra="allow"
        for Pydantic to save additional fields that are not defined in the model.
        Since the ID token can have additional fields defined in the app registration portal.
        To access these fields (if any), use the `__pydantic_extra__` attribute of the object.
        https://docs.pydantic.dev/latest/concepts/models/#extra-fields
    """

    @classmethod
    def parse_obj_debug(cls: type[AuthModel], to_parse: StrsDict) -> AuthModel:
        debug_model: AuthModel = cls.model_validate(obj=to_parse)
        debug_model.__setattr__("_recieved", to_parse)
        return debug_model

    async def save_to_session(self: AuthModel, session: SessionManager) -> None:
        session.save(self)

    @classmethod
    async def load_from_session(cls: type[AuthModel], session: SessionManager) -> Optional[AuthModel]:
        return session.load(model_cls=cls)
