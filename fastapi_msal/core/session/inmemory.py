import json

from ..utils import OptStrsDict, StrsDict
from .base import SessionBackend


class InMemorySessionBackend(SessionBackend):
    """A session backend implementation which stores session data in-memory via
    a dict.

    All methods are effectively synchronous, so locking does not need to happen.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cache_db: StrsDict = {}

    async def write(self, key: str, value: StrsDict) -> None:
        value_json: str = json.dumps(value)
        self.cache_db.update({key: value_json})

    async def read(self, key: str) -> OptStrsDict:
        value_json = self.cache_db.get(key, None)
        if value_json:
            return json.loads(value_json)
        return None

    async def remove(self, key: str) -> None:
        self.cache_db.pop(key, None)
