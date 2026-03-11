from tests.utils import create_user, get_auth_headers, create_project


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

def test_user_can_list_own_projects(client):
    create_user(client, "user@example.com", "user", "UserPass1!")
    headers = get_auth_headers(client, "user", "UserPass1!")

    create_project(client, headers, key="PR1")
    create_project(client, headers, key="PR2")

    response = client.get("/projects/", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    keys = {p["key"] for p in data}

    assert "PR1" in keys
    assert "PR2" in keys

def test_user_only_sees_projects_where_member(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    create_user(client, "other@example.com", "other", "OtherPass1!")

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")
    other_headers = get_auth_headers(client, "other", "OtherPass1!")

    create_project(client, owner_headers, key="OWN1")

    response = client.get("/projects/", headers=other_headers)

    assert response.status_code == 200
    assert response.json() == []

def test_user_can_get_project_by_id(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")

    headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project = create_project(client, headers, key="PRJ1")
    project_id = project.json()["id"]

    response = client.get(
        f"/projects/{project_id}",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == project_id
    assert data["key"] == "PRJ1"
    assert data["owner_id"] == 1

def test_user_cannot_get_project_if_not_member(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    create_user(client, "other@example.com", "other", "OtherPass1!")

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")
    other_headers = get_auth_headers(client, "other", "OtherPass1!")

    project = create_project(client, owner_headers, key="PRJ2")
    project_id = project.json()["id"]

    response = client.get(
        f"/projects/{project_id}",
        headers=other_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions for this project"
