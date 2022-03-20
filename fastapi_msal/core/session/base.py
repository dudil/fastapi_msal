from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # msal_client_config.py imports this module, so guard against recursive imports
    from ..msal_client_config import MSALClientConfig
    from ..utils import OptStrsDict, StrsDict


class SessionBackend(ABC):
    def __init__(self, settings: MSALClientConfig):
        self.settings = settings

    @abstractmethod
    async def write(self, key: str, value: StrsDict) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def read(self, key: str) -> OptStrsDict:
        raise NotImplementedError()

    @abstractmethod
    async def remove(self, key: str) -> None:
        raise NotImplementedError()
