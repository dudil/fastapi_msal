import json
from pathlib import Path

from ..utils import OptStr, OptStrsDict, StrsDict
from .base import SessionBackend

try:
    import aiofiles
    import aiofiles.os
    import aiofiles.ospath
except ImportError:
    raise ImportError(
        "aiofiles is required for file sessions. Install it using 'pip install aiofiles'."
    )


class FileSessionBackend(SessionBackend):
    """A session backend that saves session data to the filesystem.

    aiofiles is required to use. Install it using "pip install aiofiles".

    Config:
        file_path: Path - the directory session data will be saved

    """

    async def get_file(self, key: str) -> Path:
        await aiofiles.os.makedirs(self.settings.session_file_path, exist_ok=True)
        return self.settings.session_file_path / f"{key}.json"

    async def write(self, key: str, value: StrsDict) -> None:
        file = await self.get_file(key)
        value_json: str = json.dumps(value)
        await writetext(file, value_json)

    async def read(self, key: str) -> OptStrsDict:
        file = await self.get_file(key)
        value_json = await readtext(file)
        if value_json:
            return json.loads(value_json)
        return None

    async def remove(self, key: str) -> None:
        file = await self.get_file(key)
        await aiofiles.os.remove(file)


async def readtext(path: Path) -> OptStr:
    if await aiofiles.ospath.exists(path):
        async with aiofiles.open(path) as f:
            return await f.read()
    return None


async def writetext(path: Path, text: str):
    async with aiofiles.open(path) as f:
        await f.write(text)
