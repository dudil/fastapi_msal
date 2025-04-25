from urllib.parse import parse_qs, urlparse

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware

from fastapi_msal import MSALAuthorization, MSALClientConfig


@pytest.fixture
def dummy_client_config():
    return MSALClientConfig()


def test_return_to_path(dummy_client_config):
    auth = MSALAuthorization(client_config=dummy_client_config, return_to_path="https://www.example.com")

    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="")
    app.include_router(auth.router)
    client = TestClient(app, follow_redirects=False)
    response = client.get(app.url_path_for("_logout_route"))
    assert response.is_redirect

    redirect = urlparse(response.headers.get("Location"))
    assert parse_qs(redirect.query)["post_logout_redirect_uri"][0] == "https://www.example.com"


def test_referer_precedence_over_return_to_path(dummy_client_config):
    auth = MSALAuthorization(client_config=dummy_client_config, return_to_path="https://www.example.com")

    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="")
    app.include_router(auth.router)
    client = TestClient(app, follow_redirects=False)
    response = client.get(app.url_path_for("_logout_route"), headers={"Referer": "https://github.com/dudil/fastapi_msal"})
    assert response.is_redirect

    redirect = urlparse(response.headers.get("Location"))
    assert parse_qs(redirect.query)["post_logout_redirect_uri"][0] == "https://github.com/dudil/fastapi_msal"


def test_callback_url_takes_precedence_over_referer(dummy_client_config):
    auth = MSALAuthorization(client_config=dummy_client_config, return_to_path="https://www.example.com")

    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="")
    app.include_router(auth.router)
    print(app.routes)
    client = TestClient(app, follow_redirects=False)
    response = client.get(
        app.url_path_for("_logout_route"),
        headers={"Referer": "https://github.com/dudil/fastapi_msal"},
        params={"callback_url": "https://pypi.org/project/fastapi-msal"},
    )
    assert response.is_redirect

    redirect = urlparse(response.headers.get("Location"))
    assert parse_qs(redirect.query)["post_logout_redirect_uri"][0] == "https://pypi.org/project/fastapi-msal"
