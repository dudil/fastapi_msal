"""
FastAPI/MSAL - The MSAL (Microsoft Authentication Library) plugin for FastAPI!

FastAPI - https://github.com/tiangolo/fastapi
MSAL for Python - https://github.com/AzureAD/microsoft-authentication-library-for-python
"""

from .auth import MSALAuthorization as MSALAuthorization
from .core import MSALClientConfig as MSALClientConfig
from .models import AuthToken as AuthToken
from .models import IDTokenClaims as IDTokenClaims
from .models import UserInfo as UserInfo
