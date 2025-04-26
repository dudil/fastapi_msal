from urllib.parse import parse_qs, urlparse

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware

from fastapi_msal import MSALAuthorization, MSALClientConfig


@pytest.fixture
def auth():
    return MSALAuthorization(client_config=MSALClientConfig(), return_to_path="https://www.example.com")


@pytest.fixture
def app(auth):
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="")
    app.include_router(auth.router)
    return app


class TestLogoutRedirect:
    def post_logout_redirect_for(self, response):
        redirect = urlparse(response.headers.get("Location"))
        return parse_qs(redirect.query)["post_logout_redirect_uri"][0]

    @pytest.fixture
    def get_logout(self, app):
        def http_get_logout(*, headers=None, params=None):
            client = TestClient(app, follow_redirects=False)
            return client.get(app.url_path_for("_logout_route"), headers=headers, params=params)

        return http_get_logout

    def test_return_to_path(self, get_logout):
        response = get_logout()
        assert response.is_redirect
        assert self.post_logout_redirect_for(response) == "https://www.example.com"

    def test_referer_precedence_over_return_to_path(self, get_logout):
        response = get_logout(headers={"Referer": "https://github.com/dudil/fastapi_msal"})
        assert response.is_redirect
        assert self.post_logout_redirect_for(response) == "https://github.com/dudil/fastapi_msal"

    def test_callback_url_takes_precedence_over_referer(self, get_logout):
        response = get_logout(
            headers={"Referer": "https://github.com/dudil/fastapi_msal"},
            params={"callback_url": "https://pypi.org/project/fastapi-msal"},
        )
        assert response.is_redirect
        assert self.post_logout_redirect_for(response) == "https://pypi.org/project/fastapi-msal"
