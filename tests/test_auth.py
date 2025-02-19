import uuid
from datetime import date
from urllib.parse import parse_qs, urlparse

import pytest_asyncio

from app.models import models_core
from app.utils.examples import examples_auth
from app.utils.types.floors_type import FloorsType

# We need to import event_loop for pytest-asyncio routine defined bellow
from tests.commons import event_loop  # noqa
from tests.commons import add_object_to_db, client


@pytest_asyncio.fixture(scope="module", autouse=True)
async def init_objects():
    user = models_core.CoreUser(
        id=str(uuid.uuid4()),
        email="email@myecl.fr",
        password_hash="$2b$13$laYmIYSoJxqtNSQZyXu7juK8LXkOAuA8y6FZ8vzEBpV.gq2sBOxTu",  # "azerty"
        name="Fabristpp",
        firstname="Antoine",
        nickname="Nickname",
        birthday=date.fromisoformat("2000-01-01"),
        floor=FloorsType.Autre,
        created_on=date.fromisoformat("2000-01-01"),
    )
    await add_object_to_db(user)


# def test_simple_token():
#    response = client.post(
#        "/auth/simple_token",
#        data={
#            "username": "email@myecl.fr",
#            "password": "azerty",
#        },
#    )
#    assert response.status_code == 200
#    json = response.json()
#
#    # Response data validation
#    assert "access_token" in json
#    assert json["token_type"] == "bearer"
#
#    # access_token validation
#    response = client.get(
#        "/users/", headers={"Authorization": f"Bearer {json['access_token']}"}
#    )
#    assert response.status_code != 401  # unauthorized
#    assert response.status_code != 403  # forbidden


def test_authorization_code_flow_PKCE():
    code_verifier = "AntoineMonBelAntoine"
    code_challenge = "ws9GS3kBIFwDfNghvEk7GRlDvbUkSmZen8q2R4v3lBU="  # base64.urlsafe_b64encode(hashlib.sha256("AntoineMonBelAntoine".encode()).digest())
    data = examples_auth.example_AuthorizeValidation
    data["code_challenge"] = code_challenge
    response = client.post(
        "/auth/authorization-flow/authorize-validation",
        data=data,
        follow_redirects=False,
    )
    assert response.status_code == 302

    url = urlparse(response.headers["Location"])
    query = parse_qs(url.query)
    assert (url.path, query["state"][0]) == ("/docs", "azerty")
    assert query["code"][0] is not None
    code = query["code"][0]

    data = examples_auth.example_TokenReq_access_token
    data["code"] = code
    data["code_verifier"] = code_verifier

    response = client.post("/auth/token", data=data)
    assert response.status_code == 200
    json = response.json()

    assert json["access_token"] is not None
    assert json["token_type"] == "bearer"
    assert json["expires_in"] == 1800
    assert json["refresh_token"] is not None

    refresh_token = json["refresh_token"]
    data = examples_auth.example_TokenReq_refresh_token
    data["refresh_token"] = refresh_token
    response = client.post("/auth/token", data=data)

    assert response.status_code == 200
    json = response.json()
    assert json["refresh_token"] is not None

    used_refresh_token = refresh_token
    valid_refresh_token = json["refresh_token"]

    data = examples_auth.example_TokenReq_refresh_token
    data["refresh_token"] = used_refresh_token
    data["client_secret"] = "secret"
    response = client.post("/auth/token", data=data)  # Try token reuse

    assert response.status_code == 400

    data = examples_auth.example_TokenReq_refresh_token
    data["refresh_token"] = valid_refresh_token
    data["client_secret"] = "secret"
    response = client.post(
        "/auth/token", data=data
    )  # Verify that the token has been revoked due to the reuse attempt

    assert response.status_code == 400
