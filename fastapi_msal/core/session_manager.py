from typing import Optional, TypeVar, Type
from pydantic import BaseModel
from fastapi import Request

from .session import SessionBackend
from .utils import OptStr, StrsDict, OptStrsDict

M = TypeVar("M", bound=BaseModel)
SESSION_KEY: str = "sid"


class SessionManager:
    def __init__(self, request: Request, backend: SessionBackend):
        self.request = request
        self.backend = backend

    @property
    def session_id(self) -> OptStr:
        return self.request.session.get(SESSION_KEY, None)

    def init_session(self, session_id: str) -> None:
        self.request.session.update({SESSION_KEY: session_id})

    async def _read_session(self) -> OptStrsDict:
        if not self.session_id:
            return None
        session: OptStrsDict = await self.backend.read(self.session_id)
        if session:
            return session
        return dict()  # return empty session object

    async def _write_session(self, session: StrsDict) -> None:
        if not self.session_id:
            raise IOError(
                "No session id, (Make sure you initialized the session by calling init_session)"
            )
        await self.backend.write(key=self.session_id, value=session)

    async def save(self, model: M) -> None:
        session: OptStrsDict = await self._read_session()
        if session is None:
            raise IOError(
                "No session id, (Make sure you initialized the session by calling init_session)"
            )
        session.update(
            {model.__repr_name__(): model.json(exclude_none=True, by_alias=True)}
        )
        await self._write_session(session=session)

    async def load(self, model_cls: Type[M]) -> Optional[M]:
        session: OptStrsDict = await self._read_session()
        if session:
            raw_model: OptStr = session.get(model_cls.__name__, None)
            if raw_model:
                return model_cls.parse_raw(raw_model)
        return None

    async def clear(self) -> None:
        session_id = self.session_id
        if not session_id:
            return  # there is no session to clear
        # clear the session object from cache
        await self.backend.remove(session_id)
        # clear the session_id from the session cookie
        self.request.session.pop(SESSION_KEY, None)
