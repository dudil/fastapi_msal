from typing import Optional, TypeVar, Type
from enum import Enum
import json
from pydantic import BaseModel
from fastapi import Request
from .utils import OptStr, StrsDict, OptStrsDict

M = TypeVar("M", bound=BaseModel)
SESSION_KEY: str = "sid"


class CacheType(Enum):
    COOKIE = 1
    IN_MEMORY = 2
    FILE = 3


class CacheManager:
    cache_db: StrsDict = dict()

    def __init__(self):
        pass

    @classmethod
    def write(
        cls, key: str, value: StrsDict
    ) -> None:  # TODO: make sure we run this one at a time
        value_json: str = json.dumps(value)
        cls.cache_db.update({key: value_json})

    @classmethod
    def read(
        cls, key: str
    ) -> Optional[StrsDict]:  # TODO: make sure we run this one at a time
        value_json: OptStr = cls.cache_db.get(key, None)
        if value_json:
            return json.loads(value_json)
        return None

    @classmethod
    def remove(cls, key: str) -> None:  # TODO: make sure we run this one at a time
        cls.cache_db.pop(key, None)


class SessionManager:
    def __init__(self, request: Request):
        self.request = request
        self.cache_manager = CacheManager

    @property
    def session_id(self) -> OptStr:
        return self.request.session.get(SESSION_KEY, None)

    def init_session(self, session_id: str) -> None:
        self.request.session.update({SESSION_KEY: session_id})

    def _read_session(self) -> OptStrsDict:
        if not self.session_id:
            return None
        session: OptStrsDict = self.cache_manager.read(self.session_id)
        if session:
            return session
        return dict()  # return empty session object

    def _write_session(self, session: StrsDict) -> None:
        if not self.session_id:
            raise IOError(
                "No session id, (Make sure you initialized the session by calling init_session)"
            )
        self.cache_manager.write(key=self.session_id, value=session)

    def save(self, model: M) -> None:
        session: StrsDict = self._read_session()
        session.update(
            {model.__repr_name__(): model.json(exclude_none=True, by_alias=True)}
        )
        self._write_session(session=session)

    def load(self, model_cls: Type[M]) -> Optional[M]:
        session: OptStrsDict = self._read_session()
        if session:
            raw_model: OptStr = session.get(model_cls.__name__, None)
            if raw_model:
                return model_cls.parse_raw(raw_model)
        return None

    def clear(self) -> None:
        session_id = self.session_id
        if not session_id:
            return  # there is no session to clear
        # clear the session object from cache
        self.cache_manager.remove(session_id)
        # clear the session_id from the session cookie
        self.request.session.pop(SESSION_KEY, None)
