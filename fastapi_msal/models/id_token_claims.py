from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi_msal.core import OptStr, MSALPolicies
from .user_info import UserInfo


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

    msal_policy: Optional[MSALPolicies] = Field(None, alias="tfp")
    """
    This is the name of the policy that was used to acquire the token.
    """
