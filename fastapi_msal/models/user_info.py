from typing import Optional

from pydantic import BaseModel, Field

from fastapi_msal.core import OptStr, OptStrList


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
