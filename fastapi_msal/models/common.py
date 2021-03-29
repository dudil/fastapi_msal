from pydantic import BaseModel
from fastapi_msal.core import StrsDict, OptStr


class BarrierToken(BaseModel):
    token: str
    token_type: str = "bearer"

    def generate_header(self) -> StrsDict:
        return {"Authorization": f"{self.token_type} {self.token}"}


class AuthResponse(BaseModel):
    state: OptStr = None
    code: OptStr = None
