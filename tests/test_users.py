def test_create_user_success(client):
    response = client.post(
        "/users/",
        json={
            "email": "gasper@example.com",
            "username": "gasper",
            "password": "MojeGeslo1!",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "gasper@example.com"
    assert data["username"] == "gasper"
    assert data["is_active"] is True
    assert "hashed_password" not in data

def test_create_user_rejects_weak_password(client):
    response = client.post(
        "/users/",
        json={
            "email": "weak@example.com",
            "username": "weakuser",
            "password": "password",
        },
    )

    assert response.status_code == 422