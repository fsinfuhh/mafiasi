from pathlib import Path

import responses
from freezegun import freeze_time
from responses import matchers

from mafiasi.vault.vw_admin import UserStatus, VwAdminClient

BASE_DIR = Path(__file__).parent


def register_auth_response():
    responses.post(
        url="https://vault.example.com/admin/",
        match=[matchers.urlencoded_params_matcher({"token": "foobar123"})],
        headers={
            "set-cookie": "VW_ADMIN=super-secret-access-cookie; HttpOnly; sameSite=Strict; Path=/admin; Max-Age=1200",
        },
    )


@responses.activate
def test_client_auth():
    # arrange
    client = VwAdminClient.init_from_settings()
    register_auth_response()

    # act
    client.authenticate()

    # assert
    assert client.session.cookies.get("VW_ADMIN") == "super-secret-access-cookie"


@responses.activate
def test_client_auth_renew():
    # arrange
    with freeze_time("2022-01-01 12:00:00"):
        client = VwAdminClient.init_from_settings()
        client.session.cookies.set("VW_ADMIN", "super-secret-access-cookie-old", expires="60")
        register_auth_response()

    # act
    with freeze_time("2022-01-01 18:00:00"):
        client.ensure_authentication()

        # assert
        assert client.session.cookies.get("VW_ADMIN") == "super-secret-access-cookie"


@responses.activate
def test_list_users():
    # arrange
    client = VwAdminClient.init_from_settings()
    register_auth_response()
    with open(BASE_DIR / "user_list_response.json", mode="r", encoding="UTF-8") as f:
        responses.get(
            url="https://vault.example.com/admin/users",
            body=f.read(),
        )

    # act
    users = client.list_users()

    # assert
    assert len(users) == 1
    assert users[0].email == "test@example.com"
    assert users[0].status == UserStatus.ENABLED
    assert len(users[0].organizations) == 1
    assert users[0].organizations[0].name == "test-org"


@responses.activate
def test_invite():
    # arrange
    client = VwAdminClient.init_from_settings()
    register_auth_response()
    with open(BASE_DIR / "invite_response.json", mode="r", encoding="UTF-8") as f:
        responses.post(
            url="https://vault.example.com/admin/invite/",
            body=f.read(),
            match=[matchers.json_params_matcher({"email": "test@invalid.invalid"})],
        )

    # act
    response = client.invite_user("test@invalid.invalid")

    # assert
    assert response.email == "test@invalid.invalid"
    assert response.status == UserStatus.INVITED
