# FastAPI/MSAL - MSAL (Microsoft Authentication Library) plugin for FastAPI
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Lint & Security](https://github.com/dudil/fastapi_msal/actions/workflows/lint.yml/badge.svg)](https://github.com/dudil/fastapi_msal/actions/workflows/lint.yml)
[![Download monthly](https://pepy.tech/badge/fastapi_msal/month)](https://pypistats.org/packages/fastapi_msal)

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
1. Include a dependency class to authenticate and secure your application APIs
1. Includes a pydantic setting class for easy and secure configuration from your ENV (or .env or secrets directory)
1. Full support with FastAPI swagger documentations and authentication simulation

## Installation

```shell
pip install "fastapi_msal"
```
Or if you wish to have all the required packages straight forward
```shell
pip install "fastapi_msal[full]"
```

## Prerequisets
1. Python 3.9 and above
2. As part of your fastapi application the following packages should be included:  
(if you use the **[full]** method it is not required.)
   1. [python-multipart](https://andrew-d.github.io/python-multipart/),
   _[From FastAPI documentation](https://fastapi.tiangolo.com/tutorial/security/first-steps/#run-it)_:
   This is required since OAuth2 (Which MSAL is based upon) uses "form data" to send the credentials.

   2. [itsdangerous](https://github.com/pallets/itsdangerous)
   Used by Starlette [session middleware](https://www.starlette.io/middleware/)

## Usage
1. Follow the application [registration process
with the Microsoft Identity Platform](https://docs.microsoft.com/azure/active-directory/develop/quickstart-v2-register-an-app). Finishing the processes will allow you to [register your app callback path with the platform](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app#add-a-redirect-uri), as well as to retrieve your application `client_id`, `tenant_id` and `client_credential` ([client secrets](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app#add-credentials)) - see images below:

![Client and tenant ID page](docs/images/client_tenant_id_page.png)

![Client secrets page](docs/images/client_secrets_page.png)

2. Create a new main.py file and add the following lines.
Make sure to update the lines with the information retrieved in the previous step
``` python
import uvicorn
from fastapi import FastAPI, Depends
from starlette.middleware.sessions import SessionMiddleware
from fastapi_msal import MSALAuthorization, UserInfo, MSALClientConfig

client_config: MSALClientConfig = MSALClientConfig()
client_config.client_id = "The client_id retrieved at step #1"
client_config.client_credential = "The client_credential retrieved at step #1"
client_config.tenant = "Your tenant_id retrieved at step #1"

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="SOME_SSH_KEY_ONLY_YOU_KNOW")  # replace with your own!!!
msal_auth = MSALAuthorization(client_config=client_config)
app.include_router(msal_auth.router)


@app.get("/users/me", response_model=UserInfo, response_model_exclude_none=True, response_model_by_alias=False)
async def read_users_me(current_user: UserInfo = Depends(msal_auth.scheme)) -> UserInfo:
    return current_user


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=5000, reload=True)
```

3. Run your app
```shell
(pipenv shell)$ python main.py
INFO:     Uvicorn running on http://localhost:5000 (Press CTRL+C to quit)
INFO:     Started reloader process [12785] using statreload
INFO:     Started server process [12787]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

4. Browse to http://localhost:5000/docs - this is the API docs generated by FastAPI (totaly cool!)
![Document Page Image](https://github.com/dudil/fastapi_msal/blob/master/docs/images/authorize_page.png?raw=true/blob/images/docs_page.png?raw=true)

5. Using the "built-in" authenticaiton button (the little lock) you will be able to set the full authentication process
![Authorize Page Image](https://github.com/dudil/fastapi_msal/blob/master/docs/images/authorize_page.png?raw=true)
   (Ignore the client_id and client_secret - they are not relevant for the process as you already set them)

6. After you complete the process you will get a confirmation popup
![Token Page Image](https://github.com/dudil/fastapi_msal/blob/master/docs/images/token_page.png?raw=true)

7. Trying out the _ME_ api endpoint
![Me Page Image](https://github.com/dudil/fastapi_msal/blob/master/docs/images/me_page.png?raw=true)

## Working Example/Template
If you wish to try out a working example, clone the following project and adjust it to your needs:
[https://github.com/dudil/ms-identity-python-webapp](https://github.com/dudil/ms-identity-python-webapp)

**NB!** Make sure you are using the *fastapi_msal* branch!!!
