from tests.utils import create_user, get_auth_headers


def test_owner_can_add_project_member(client):
    create_user(
        client,
        email="owner@example.com",
        username="owner",
        password="OwnerPass1!",
    )
    create_user(
        client,
        email="member@example.com",
        username="member",
        password="MemberPass1!",
    )

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    create_project_response = client.post(
        "/projects/",
        json={
            "name": "Issue Tracker Backend",
            "key": "ITB",
            "description": "Backend API project",
        },
        headers=owner_headers,
    )
    project_id = create_project_response.json()["id"]

    add_member_response = client.post(
        f"/projects/{project_id}/members",
        json={
            "user_id": 2,
            "role": "member",
        },
        headers=owner_headers,
    )

    assert add_member_response.status_code == 201
    data = add_member_response.json()
    assert data["project_id"] == project_id
    assert data["user_id"] == 2
    assert data["role"] == "member"

def test_cannot_add_same_member_twice(client):
    create_user(
        client,
        email="owner@example.com",
        username="owner",
        password="OwnerPass1!",
    )
    create_user(
        client,
        email="member@example.com",
        username="member",
        password="MemberPass1!",
    )

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    create_project_response = client.post(
        "/projects/",
        json={
            "name": "Issue Tracker Backend",
            "key": "ITB",
            "description": "Backend API project",
        },
        headers=owner_headers,
    )
    project_id = create_project_response.json()["id"]

    first_response = client.post(
        f"/projects/{project_id}/members",
        json={"user_id": 2, "role": "member"},
        headers=owner_headers,
    )

    second_response = client.post(
        f"/projects/{project_id}/members",
        json={"user_id": 2, "role": "member"},
        headers=owner_headers,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "User is already a member of this project"

def test_member_cannot_add_project_member(client):
    create_user(
        client,
        email="owner@example.com",
        username="owner",
        password="OwnerPass1!",
    )
    create_user(
        client,
        email="member@example.com",
        username="member",
        password="MemberPass1!",
    )
    create_user(
        client,
        email="other@example.com",
        username="other",
        password="OtherPass1!",
    )

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")
    member_headers = get_auth_headers(client, "member", "MemberPass1!")

    create_project_response = client.post(
        "/projects/",
        json={
            "name": "Issue Tracker Backend",
            "key": "ITB",
            "description": "Backend API project",
        },
        headers=owner_headers,
    )
    project_id = create_project_response.json()["id"]

    client.post(
        f"/projects/{project_id}/members",
        json={"user_id": 2, "role": "member"},
        headers=owner_headers,
    )

    forbidden_response = client.post(
        f"/projects/{project_id}/members",
        json={"user_id": 3, "role": "member"},
        headers=member_headers,
    )

    assert forbidden_response.status_code == 403
    assert forbidden_response.json()["detail"] == "Not enough permissions for this action"

def test_non_member_cannot_list_project_members(client):
    create_user(
        client,
        email="owner@example.com",
        username="owner",
        password="OwnerPass1!",
    )
    create_user(
        client,
        email="outsider@example.com",
        username="outsider",
        password="OutsiderPass1!",
    )

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")
    outsider_headers = get_auth_headers(client, "outsider", "OutsiderPass1!")

    create_project_response = client.post(
        "/projects/",
        json={
            "name": "Issue Tracker Backend",
            "key": "ITB",
            "description": "Backend API project",
        },
        headers=owner_headers,
    )
    project_id = create_project_response.json()["id"]

    response = client.get(
        f"/projects/{project_id}/members",
        headers=outsider_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions for this project"