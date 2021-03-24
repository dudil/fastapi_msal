from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from fastapi_msal.core import OptStr


class AuthClaims(BaseModel):
    auth_time: Optional[datetime] = None
    """Time when the user last authenticated. See OpenID Connect spec."""
    sid: OptStr = None
    """Session ID, used for per-session user sign-out."""
    verified_primary_email: OptStr = None
    """Sourced from the user's PrimaryAuthoritativeEmail"""
    verified_secondary_email: OptStr = None
    """Sourced from the user's SecondaryAuthoritativeEmail"""
    vnet: OptStr = None
    """VNET specifier information"""
    fwd: OptStr = None
    """IP addresses"""
    acct: OptStr = None
    """"""
    groups: OptStr = None
    """"""
    upn: OptStr = None
    """"""
    idtyp: OptStr = None
    """"""
    ipaddr: OptStr = None
    """"""
