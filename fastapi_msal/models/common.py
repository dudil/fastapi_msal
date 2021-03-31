from pydantic import BaseModel
from fastapi_msal.core import StrsDict, OptStr


class BearerToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

    def generate_header(self) -> StrsDict:
        return {"Authorization": f"{self.token_type} {self.access_token}"}


class AuthResponse(BaseModel):
    state: OptStr = None
    code: OptStr = None
