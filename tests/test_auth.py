from tests.utils import create_user, login_user, get_auth_headers


def test_login_success(client):
    create_user(
        client,
        email="gasper@example.com",
        username="gasper",
        password="MojeGeslo1!",
    )

    response = login_user(
        client,
        username="gasper",
        password="MojeGeslo1!",
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    create_user(
        client,
        email="gasper@example.com",
        username="gasper",
        password="MojeGeslo1!",
    )

    response = login_user(
        client,
        username="gasper",
        password="WrongPass1!",
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_read_current_user_requires_auth(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_read_current_user_success(client):
    create_user(
        client,
        email="gasper@example.com",
        username="gasper",
        password="MojeGeslo1!",
    )

    headers = get_auth_headers(client, "gasper", "MojeGeslo1!")
    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "gasper"
    assert data["email"] == "gasper@example.com"