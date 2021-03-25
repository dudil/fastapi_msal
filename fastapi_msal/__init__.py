"""
FastAPI/MSAL - The MSAL (Microsoft Authentication Library) plugin for FastAPI!

FastAPI - https://github.com/tiangolo/fastapi
MSAL for Python - https://github.com/AzureAD/microsoft-authentication-library-for-python
"""

__version__ = "0.0.1"

from .core import MSALPolicies
from .models import UserInfo, IDTokenClaims
from .auth import MSALAuthorization
