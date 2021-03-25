from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, PrivateAttr, Field

from fastapi_msal.core import MSALPolicies, OptStr, StrsDict, OptStrsDict, OptStrList


class UserInfo(BaseModel):
    first_name: OptStr = Field(None, alias="given_name")
    """
    The user's given name (also known as first name).
    """

    last_name: OptStr = Field(None, alias="family_name")
    """
    The user's surname (also known as last name).
    """

    display_name: OptStr = Field(None, alias="name")
    """
    The user's full name in displayable form including all name parts, possibly including titles and suffixes.
    """

    city: OptStr = None
    """
    The user's city
    """

    country: OptStr = None
    """
    The user's country
    """

    postal_code: OptStr = Field(None, alias="postalCode")
    """
    The user's postal code (or zip code)
    """

    street_address: OptStr = Field(None, alias="streetAddress")
    """
    The user's street address
    """

    emails: OptStrList = None
    """
    Email addresses of the user. These are mutable and might change over time.
    Therefore, they are not suitable for identifying the user in other databases or applications.
    The oid or sub claim should be used instead.
    """


class AADInternalClaims(BaseModel):
    aio: OptStr = None
    """
    An internal claim used by Azure AD to record data for token reuse. Resources should not use this claim.
    """

    rh: OptStr = None
    """
    An internal claim used by Azure to revalidate tokens. Resources should not use this claim.
    """

    uti: OptStr = None
    """
    An internal claim used by Azure to revalidate tokens. Resources shouldn't use this claim.
    """


class IDTokenClaims(UserInfo, AADInternalClaims):
    exp: Optional[datetime] = None
    """
    The expiration time claim is the time at which the token becomes invalid, represented in epoch time.
    Your app should use this claim to verify the validity of the token lifetime.
    """

    not_before: Optional[datetime] = Field(None, alias="nbf")
    """
    This claim is the time at which the token becomes valid, represented in epoch time.
    This is usually the same as the time the token was issued.
    Your app should use this claim to verify the validity of the token lifetime.
    """

    ver: OptStr = None
    """
    Indicates the version of the token.
    """

    issuer: OptStr = Field(None, alias="iss")
    """
    This claim identifies the fastpi_msal token service (STS) that constructs and returns the token.
    It also identifies the Azure AD directory in which the user was authenticated.
    Your app should validate the issuer claim to ensure that the token came from the v2.0 endpoint.
    It also should use the GUID portion of the claim to restrict the set of tenants that can sign in to the app.
    """

    subject: OptStr = Field(None, alias="sub")
    """
    This is the principal about which the token asserts information, such as the user of an app.
    This value is immutable and cannot be reassigned or reused.
    It can be used to perform authorization checks safely, such as when the token is used to access a resource.
    By default, the subject claim is populated with the object ID of the user in the directory.
    To learn more: https://docs.microsoft.com/en-us/azure/active-directory-b2c/active-directory-b2c-token-session-sso
    """

    audience: OptStr = Field(None, alias="aud")
    """
    An audience claim identifies the intended recipient of the token.
    For Azure AD B2C, the audience is your app's Application ID, as assigned to your app in the app registration portal.
    Your app should validate this value and reject the token if it does not match.
    """

    nonce: OptStr = None
    """
    A nonce is a strategy used to mitigate token replay attacks.
    Your app can specify a nonce in an authorization request by using the nonce query parameter.
    The value you provide in the request will be emitted unmodified in the nonce claim of an ID token only.
    This allows your app to verify the value against the value it specified on the request,
    which associates the app's session with a given ID token.
    Your app should perform this validation during the ID token validation process.
    """

    issue_time: Optional[datetime] = Field(None, alias="iat")
    """
    The time at which the token was issued, represented in epoch time.
    """

    auth_time: Optional[datetime] = None
    """
    This claim is the time at which a user last entered credentials, represented in epoch time.
    """

    user_id: OptStr = Field(None, alias="oid")
    """
    The immutable identifier for the user account in the tenant.
    It can be used to perform authorization checks safely and as a key in database tables.
    This ID uniquely identifies the user across applications -
    two different applications signing in the same user will receive the same value in the oid claim.
    This means that it can be used when making queries to Microsoft online services, such as the Microsoft Graph.
    The Microsoft Graph will return this ID as the id property for a given user account.
    """

    preferred_username: OptStr = None
    """
    The primary username that represents the user. 
    It could be an email address, phone number, or a generic username without a specified format. 
    Its value is mutable and might change over time. 
    Since it is mutable, this value must not be used to make authorization decisions. 
    It can be used for username hints, however, and in human-readable UI as a username. 
    The profile scope is required in order to receive this claim. Present only in v2.0 tokens.
    """

    is_new_user: Optional[bool] = Field(None, alias="newUser")
    """
    Indicated if this is a new user in the system (following a registration on AAD web part e.g.)
    """

    msal_policy: Optional[MSALPolicies] = Field(None, alias="tfp")
    """
    This is the name of the policy that was used to acquire the token.
    """

    _received: OptStr = PrivateAttr(None)
    """
    the object as received from MSAL API - for debug purposes only!
    TODO: This is for debug purposes only. should be removed in production code
    """


class AuthToken(BaseModel):
    id_token: OptStr = None
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
    The scopes that the access_token is valid for. 
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

    _received: OptStrsDict = PrivateAttr()
    """
    the object as received from MSAL API - for debug purposes only!
    TODO: This is for debug purposes only. should be removed in production code
    """

    @classmethod
    def parse_dict(cls: AuthToken, to_parse: StrsDict) -> AuthToken:
        auth_token: AuthToken = cls.parse_obj(to_parse)
        auth_token._received = to_parse
        if auth_token.id_token_claims:
            auth_token.id_token_claims._received = to_parse.get("id_token_claims", None)
        return auth_token
