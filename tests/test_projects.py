from tests.utils import create_user, get_auth_headers


def test_create_project_success(client):
    create_user(
        client,
        email="owner@example.com",
        username="owner",
        password="OwnerPass1!",
    )
    headers = get_auth_headers(client, "owner", "OwnerPass1!")

    response = client.post(
        "/projects/",
        json={
            "name": "Issue Tracker Backend",
            "key": "ITB",
            "description": "Backend API project",
        },
        headers=headers,
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Issue Tracker Backend"
    assert data["key"] == "ITB"
    assert data["owner_id"] == 1

def test_create_project_requires_auth(client):
    response = client.post(
        "/projects/",
        json={
            "name": "Issue Tracker Backend",
            "key": "ITB",
            "description": "Backend API project",
        },
    )

    assert response.status_code == 401

def test_create_project_duplicate_key_fails(client):
    create_user(
        client,
        email="owner@example.com",
        username="owner",
        password="OwnerPass1!",
    )
    headers = get_auth_headers(client, "owner", "OwnerPass1!")

    payload = {
        "name": "Issue Tracker Backend",
        "key": "ITB",
        "description": "Backend API project",
    }

    first_response = client.post("/projects/", json=payload, headers=headers)
    second_response = client.post("/projects/", json=payload, headers=headers)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Project key already exists"

def test_project_creator_is_added_as_owner_member(client):
    create_user(
        client,
        email="owner@example.com",
        username="owner",
        password="OwnerPass1!",
    )
    headers = get_auth_headers(client, "owner", "OwnerPass1!")

    create_response = client.post(
        "/projects/",
        json={
            "name": "Issue Tracker Backend",
            "key": "ITB",
            "description": "Backend API project",
        },
        headers=headers,
    )

    project_id = create_response.json()["id"]

    members_response = client.get(f"/projects/{project_id}/members", headers=headers)

    assert members_response.status_code == 200

    members = members_response.json()
    assert len(members) == 1
    assert members[0]["user_id"] == 1
    assert members[0]["role"] == "owner"