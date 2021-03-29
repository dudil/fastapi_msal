# FastAPI/MSAL - MSAL (Microsoft Authentication Library) plugin for FastAPI
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with Pylint](https://github.com/dudil/fastapi_msal/actions/workflows/lint.yml/badge.svg)](https://github.com/dudil/fastapi_msal/actions/workflows/lint.yml)

FastAPI - https://github.com/tiangolo/fastapi  
_FastAPI is a modern, fast (high-performance), web framework for building APIs based on standard Python type hints._  

MSAL for Python - https://github.com/AzureAD/microsoft-authentication-library-for-python  
_The Microsoft Authentication Library for Python enables applications to integrate with the 
[Microsoft identity platform.](https://aka.ms/aaddevv2)  
It allows you to sign in users or apps with Microsoft identities
and obtain tokens to call Microsoft APIs such as [Microsoft Graph](https://graph.microsoft.io/) 
or your own APIs registered with the Microsoft identity platform. 
It is built using industry standard OAuth2 and OpenID Connect protocols_

The **fastapi_msal** package was built to allow quick "out of the box" integration with MSAL.
As a result the pacage was built around simplicity and ease of use on the expense of flexability and versatility.

## Features
1. Includes Async implementation of MSAL confidential client class utilizaing Starlette threadpool model.
1. Use pydantic models to translate the MSAL objects to data objects which are code and easy to work with.
1. Have a built-in router which includes the required paths for the authentication flow.
1. Includes a pydantic setting class for easy and secure configuration from your ENV (or .env)

## Installation
With [pipenv](https://pipenv.pypa.io/en/latest/) (really, don't use anything else...)
```bash
pipenv install git+https://github.com/dudil/fastapi_msal.git#egg=fastapi_msal
```

## Prerequisets
As part of your fastapi application the following packages will also be included  
(They are not required by fastpi_msal directly hence they are listed here)
1. [python-multipart](https://andrew-d.github.io/python-multipart/)  
_[From FastAPI documentation](https://fastapi.tiangolo.com/tutorial/security/first-steps/#run-it)_:  
This is required since OAuth2 (Which MSAL is based upon) uses "form data" to send the credentials.

1. [itsdangerous](https://github.com/pallets/itsdangerous)  
Used by Starlette [session middleware](https://www.starlette.io/middleware/)

1. [python-dotenv](https://github.com/theskumar/python-dotenv)  
Used by [pydantic settings management](https://pydantic-docs.helpmanual.io/usage/settings/) 
   to read configuration from a ".env" file (Optional but recommended)

## Usage
1. You will need to follow the application [registration process
with the microsoft identity platform.](https://docs.microsoft.com/azure/active-directory/develop/quickstart-v2-register-an-app)  
Finishing the processes will allow you to retrieve your app_code and app_credentials (app_secret)
As well as register your app callback path with the platform.

2. Add the file _fastapi_msal.env_ with the following configuration.  
**NB! make sure to add all ".env" to your gitignore!!!**
```ini
CLIENT_ID="THE-APP-CLIENT-ID"
CLIENT_CREDENTIAL="THE-APP-CLIENT-CREDENTIAL/SECRET"
TENANT="YOUR-TENANT-NAME"
POLICY="ONE-OF: AAD_MULTI\AAD_SINGLE\B2C_1_LOGIN\B2C_1_PROFILE"
SCOPES=["OPTIONAL-SCOPES"]
```
The policy configuration will be used according to your application target identity platform.
If you are writing your own tenant graph-api application, you will select AAD_SINGLE.  
If you wish to log-in your users to AAD B2C you should select B2C_1_LOGIN.

3. Include the following line in your app main file:
``` python
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, PlainTextResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi_msal import MSALAuthorization, MSALClientConfig, UserInfo 

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="SOME_SSH_KEY_ONLY_YOU_KNOW")
msal_config = MSALClientConfig()
msal_auth = MSALAuthorization(client_config=msal_config)
app.include_router(msal_auth.router)

@app.get("/", response_class=PlainTextResponse)
async def index(request: Request):
    token: Optional[str] = request.session.get("AuthToken", None)
    if not token:
        return RedirectResponse(request.url_for(name="login"))
    user: UserInfo = await msal_auth.handler.parse_id_token(token=token)
    return f"Hi There {user.display_name}!"
```
## TODO List
[] Add support for local/redis session cache
