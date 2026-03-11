from tests.utils import create_user, get_auth_headers, create_project, add_project_member


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

def test_owner_can_update_project_member_role(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    create_user(client, "member@example.com", "member", "MemberPass1!")

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    create_project_response = create_project(client, owner_headers, key="MEM1")
    project_id = create_project_response.json()["id"]

    add_project_member(client, project_id, 2, "member", owner_headers)

    response = client.patch(
        f"/projects/{project_id}/members/2",
        json={"role": "admin"},
        headers=owner_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 2
    assert data["role"] == "admin"

def test_member_cannot_update_project_member_role(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    create_user(client, "member@example.com", "member", "MemberPass1!")
    create_user(client, "other@example.com", "other", "OtherPass1!")

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")
    member_headers = get_auth_headers(client, "member", "MemberPass1!")

    create_project_response = create_project(client, owner_headers, key="MEM2")
    project_id = create_project_response.json()["id"]

    add_project_member(client, project_id, 2, "member", owner_headers)
    add_project_member(client, project_id, 3, "viewer", owner_headers)

    response = client.patch(
        f"/projects/{project_id}/members/3",
        json={"role": "admin"},
        headers=member_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions for this action"

def test_cannot_change_owner_role(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    create_user(client, "admin@example.com", "admin", "AdminPass1!")

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")
    admin_headers = get_auth_headers(client, "admin", "AdminPass1!")

    create_project_response = create_project(client, owner_headers, key="MEM3")
    project_id = create_project_response.json()["id"]

    add_project_member(client, project_id, 2, "admin", owner_headers)

    response = client.patch(
        f"/projects/{project_id}/members/1",
        json={"role": "viewer"},
        headers=admin_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Owner role cannot be changed"

def test_owner_can_remove_project_member(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    create_user(client, "member@example.com", "member", "MemberPass1!")

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    create_project_response = create_project(client, owner_headers, key="MEM4")
    project_id = create_project_response.json()["id"]

    add_project_member(client, project_id, 2, "member", owner_headers)

    response = client.delete(
        f"/projects/{project_id}/members/2",
        headers=owner_headers,
    )

    assert response.status_code == 204

    members_response = client.get(
        f"/projects/{project_id}/members",
        headers=owner_headers,
    )
    members = members_response.json()

    assert len(members) == 1
    assert members[0]["user_id"] == 1
    assert members[0]["role"] == "owner"

def test_cannot_remove_owner_from_project(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    create_user(client, "admin@example.com", "admin", "AdminPass1!")

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")
    admin_headers = get_auth_headers(client, "admin", "AdminPass1!")

    create_project_response = create_project(client, owner_headers, key="MEM5")
    project_id = create_project_response.json()["id"]

    add_project_member(client, project_id, 2, "admin", owner_headers)

    response = client.delete(
        f"/projects/{project_id}/members/1",
        headers=admin_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Owner cannot be removed from the project"

def test_non_member_cannot_remove_project_member(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    create_user(client, "member@example.com", "member", "MemberPass1!")
    create_user(client, "outsider@example.com", "outsider", "OutsiderPass1!")

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")
    outsider_headers = get_auth_headers(client, "outsider", "OutsiderPass1!")

    create_project_response = create_project(client, owner_headers, key="MEM6")
    project_id = create_project_response.json()["id"]

    add_project_member(client, project_id, 2, "member", owner_headers)

    response = client.delete(
        f"/projects/{project_id}/members/2",
        headers=outsider_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions for this project"