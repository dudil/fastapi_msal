from datetime import datetime, timedelta
from typing import Optional

from fastapi_msal.core import OptStr
from .base_auth_model import BaseAuthModel
from .id_token_claims import IDTokenClaims


class AuthToken(BaseAuthModel):
    id_token: str
    """
    A JSON Web Token (JWT).
    The app can decode the segments of this token to request information about the user who signed in.
    The app can cache the values and display them, and confidential clients can use this for authorization.
    For more information about id_tokens, see the id_token reference:
    https://docs.microsoft.com/en-us/azure/active-directory/develop/id-tokens
    Note: Only provided if openid scope was requested.
    """

    id_token_claims: Optional[IDTokenClaims] = None
    """
    The decoded content of id_token
    """

    access_token: OptStr = None
    """
    The requested access token. The app can use this token to authenticate to the secured resource, such as a web API.
    https://docs.microsoft.com/en-us/azure/active-directory/develop/access-tokens
    """

    token_type: OptStr = None
    """
    Indicates the token type value. The only type that Azure AD supports is Bearer
    """

    not_before: Optional[datetime] = None
    expires_in: Optional[timedelta] = None
    """
    How long the access token is valid (in seconds).
    """

    client_info: OptStr = None
    scope: OptStr = None
    """
    The scopes that the token is valid for.
    Optional: this is non-standard, and if omitted the token will be for the scopes requested on the initial flow leg.
    """

    refresh_token: OptStr = None
    """
    An OAuth 2.0 refresh token.
    The app can use this token acquire additional access tokens after the current access token expires.
    Refresh_tokens are long-lived, and can be used to retain access to resources for extended periods of time.
    For more detail on refreshing an access token, refer to:
    https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow#refresh-the-access-token
    Note: Only provided if offline_access scope was requested.
    """

    refresh_token_expires_in: Optional[timedelta] = None

    error: OptStr = None
    """
    An error code string that can be used to classify types of errors that occur, and can be used to react to errors.
    """

    error_description: OptStr = None
    """
    A specific error message that can help a developer identify the root cause of an authentication error.
    """

    error_uri: OptStr = None
