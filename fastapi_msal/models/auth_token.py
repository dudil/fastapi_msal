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


class IDTokenClaims(UserInfo):
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
    The version of the ID token, as defined by Azure AD B2C.
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
    MSAL ID Token are JWT containing a header, payload and signature.
    https://docs.microsoft.com/en-us/azure/active-directory/develop/id-tokens
    """

    id_token_claims: Optional[IDTokenClaims] = None
    """
    The decoded content of id_token
    """

    token_type: OptStr = None
    not_before: Optional[datetime] = None
    client_info: OptStr = None
    scope: OptStr = None
    refresh_token: OptStr = None
    refresh_token_expires_in: Optional[timedelta] = None

    error: OptStr = None
    """
    returned in case of error
    """
    error_description: OptStr = None
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
