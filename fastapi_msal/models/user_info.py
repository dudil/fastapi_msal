from typing import Optional, Union

from pydantic import Field

from fastapi_msal.core import OptStr, OptStrList, StrList

from .base_auth_model import BaseAuthModel


class UserInfo(BaseAuthModel):
    preferred_username: OptStr = None
    """
    The primary username that represents the user.
    It could be an email address, phone number, or a generic username without a specified format.
    Its value is mutable and might change over time.
    Since it is mutable, this value must not be used to make authorization decisions.
    It can be used for username hints, however, and in human-readable UI as a username.
    The profile scope is required in order to receive this claim. Present only in v2.0 tokens.
    """

    email: OptStr = None
    """
    Present by default for guest accounts that have an email address.
    Your app can request the email claim for managed users (from the same tenant) using the email optional claim.
    This value isn't guaranteed to be correct and is mutable over time.
    Never use it for authorization or to save data for a user.
    On the v2.0 endpoint, your app can also request the email OpenID Connect scope -
    you don't need to request both the optional claim and the scope to get the claim.
    """

    display_name: OptStr = Field(None, alias="name")
    """
    The name claim provides a human-readable value that identifies the subject of the token.
    The value isn't guaranteed to be unique, it can be changed, and should be used only for display purposes.
    The profile scope is required to receive this claim.
    """

    first_name: OptStr = Field(None, alias="given_name")
    """
    The user's given name (also known as first name).
    """

    last_name: OptStr = Field(None, alias="family_name")
    """
    The user's surname (also known as last name).
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

    user_id: OptStr = Field(None, alias="oid")
    """
    The immutable identifier for the user account in the tenant.
    It can be used to perform authorization checks safely and as a key in database tables.
    This ID uniquely identifies the user across applications -
    two different applications signing in the same user will receive the same value in the oid claim.
    This means that it can be used when making queries to Microsoft online services, such as the Microsoft Graph.
    The Microsoft Graph will return this ID as the id property for a given user account.
    """

    unique_name: OptStr = None
    """
    Only present in v1.0 tokens. Provides a human readable value that identifies the subject of the token.
    This value isn't guaranteed to be unique within a tenant and should be used only for display purposes.
    """

    is_new_user: Optional[bool] = Field(None, alias="newUser")
    """
    Indicated if this is a new user in the system (following a registration on AAD web part e.g.)
    """

    roles: OptStrList = None
    """
    The roles claim if its present - list of strings, each indicating a role assigned to the user
    https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-add-app-roles-in-apps
    """

    hasgroups: Optional[bool] = None
    """
    If present, always true, denoting the user is in at least one group.
    Used in place of the groups claim for JWTs in implicit grant flows when the full groups claim extends-
     the URI fragment beyond the URL length limits (currently six or more groups).
    Indicates that the client should use the Microsoft Graph API to determine the user's groups
    (https://graph.microsoft.com/v1.0/users/{userID}/getMemberObjects).
    """

    groups: Union[StrList, str, None] = None
    """
    Provides object IDs that represent the group memberships of the subject.
    The groupMembershipClaims property of the application manifest configures the groups claim on a per-application basis.
    A value of null excludes all groups, a value of SecurityGroup includes only Active Directory Security Groups,
    and a value of All includes both Security Groups and Microsoft 365 Distribution Lists.

    See the hasgroups claim for details on using the groups claim with the implicit grant. For other flows,
    if the number of groups the user is in goes over 150 for SAML and 200 for JWT,
    then Microsoft Entra ID adds an overage claim to the claim sources.
    The claim sources point to the Microsoft Graph endpoint that contains the list of groups for the user.
    """
