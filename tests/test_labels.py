from tests.utils import (
    add_project_member,
    create_project,
    create_user,
    get_auth_headers,
)


def test_member_can_create_label(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    create_user(client, "member@example.com", "member", "MemberPass1!")

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")
    member_headers = get_auth_headers(client, "member", "MemberPass1!")

    project_response = create_project(client, owner_headers, key="LAB1")
    project_id = project_response.json()["id"]

    add_project_member(client, project_id, "member", "member", owner_headers)

    response = client.post(
        f"/projects/{project_id}/labels",
        json={
            "name": "backend",
            "color": "#FF5733",
        },
        headers=member_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["project_id"] == project_id
    assert data["name"] == "backend"
    assert data["color"] == "#FF5733"


def test_viewer_cannot_create_label(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    create_user(client, "viewer@example.com", "viewer", "ViewerPass1!")

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")
    viewer_headers = get_auth_headers(client, "viewer", "ViewerPass1!")

    project_response = create_project(client, owner_headers, key="LAB2")
    project_id = project_response.json()["id"]

    add_project_member(client, project_id, "viewer", "viewer", owner_headers)

    response = client.post(
        f"/projects/{project_id}/labels",
        json={
            "name": "frontend",
            "color": "#00AAFF",
        },
        headers=viewer_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions for this action"


def test_can_attach_label_to_issue(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="LAB3")
    project_id = project_response.json()["id"]

    issue_response = client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Add labels feature",
            "description": "Implement labels endpoints",
            "status": "todo",
            "priority": "high",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )
    issue_id = issue_response.json()["id"]

    label_response = client.post(
        f"/projects/{project_id}/labels",
        json={
            "name": "enhancement",
            "color": "#22CC88",
        },
        headers=owner_headers,
    )
    label_id = label_response.json()["id"]

    attach_response = client.post(
        f"/projects/{project_id}/issues/{issue_id}/labels",
        json={"label_id": label_id},
        headers=owner_headers,
    )

    assert attach_response.status_code == 201

    list_response = client.get(
        f"/projects/{project_id}/issues/{issue_id}/labels",
        headers=owner_headers,
    )

    assert list_response.status_code == 200
    labels = list_response.json()
    assert len(labels) == 1
    assert labels[0]["name"] == "enhancement"


def test_cannot_attach_same_label_twice(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="LAB4")
    project_id = project_response.json()["id"]

    issue_response = client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Duplicate attach test",
            "description": "Should fail on second attach",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )
    issue_id = issue_response.json()["id"]

    label_response = client.post(
        f"/projects/{project_id}/labels",
        json={
            "name": "bug",
            "color": "#FF0000",
        },
        headers=owner_headers,
    )
    label_id = label_response.json()["id"]

    first_response = client.post(
        f"/projects/{project_id}/issues/{issue_id}/labels",
        json={"label_id": label_id},
        headers=owner_headers,
    )

    second_response = client.post(
        f"/projects/{project_id}/issues/{issue_id}/labels",
        json={"label_id": label_id},
        headers=owner_headers,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Label is already attached to this issue"


def test_can_update_label(client):
    create_user(client, "owner@example.com", "owner", "Ownerpass1!")
    owner_headers = get_auth_headers(client, "owner", "Ownerpass1!")

    project_response = create_project(client, owner_headers, key="LAB5")
    project_id = project_response.json()["id"]

    label_response = client.post(
        f"/projects/{project_id}/labels",
        json={
            "name": "backend",
            "color": "#FF5733",
        },
        headers=owner_headers,
    )
    label_id = label_response.json()["id"]

    response = client.patch(
        f"/projects/{project_id}/labels/{label_id}",
        json={
            "name": "api",
            "color": "#00AAFF",
        },
        headers=owner_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "api"
    assert data["color"] == "#00AAFF"


def test_cannot_update_label_to_duplicate_name(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="LAB6")
    project_id = project_response.json()["id"]

    first_label = client.post(
        f"/projects/{project_id}/labels",
        json={"name": "backend", "color": "#00AAFF"},
        headers=owner_headers,
    )
    second_label = client.post(
        f"/projects/{project_id}/labels",
        json={"name": "frontend", "color": "#00AAFF"},
        headers=owner_headers,
    )

    second_label_id = second_label.json()["id"]

    response = client.patch(
        f"/projects/{project_id}/labels/{second_label_id}",
        json={"name": "backend"},
        headers=owner_headers,
    )

    assert first_label.status_code == 201
    assert second_label.status_code == 201
    assert response.status_code == 409
    assert response.json()["detail"] == "Label name already exists in this project"


def test_can_delete_label(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="LAB7")
    project_id = project_response.json()["id"]

    label_response = client.post(
        f"/projects/{project_id}/labels",
        json={
            "name": "backend",
            "color": "#FF5733",
        },
        headers=owner_headers,
    )
    label_id = label_response.json()["id"]

    delete_response = client.delete(
        f"/projects/{project_id}/labels/{label_id}",
        headers=owner_headers,
    )

    assert delete_response.status_code == 204

    list_response = client.get(
        f"/projects/{project_id}/labels",
        headers=owner_headers,
    )

    assert list_response.status_code == 200
    assert list_response.json() == []


def test_can_remove_label_from_issue(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="LAB8")
    project_id = project_response.json()["id"]

    issue_response = client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Detach label test",
            "description": "Testing label removal",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )
    issue_id = issue_response.json()["id"]

    label_response = client.post(
        f"/projects/{project_id}/labels",
        json={
            "name": "bug",
            "color": "#FF0000",
        },
        headers=owner_headers,
    )
    label_id = label_response.json()["id"]

    client.post(
        f"/projects/{project_id}/issues/{issue_id}/labels",
        json={"label_id": label_id},
        headers=owner_headers,
    )

    remove_response = client.delete(
        f"/projects/{project_id}/issues/{issue_id}/labels/{label_id}",
        headers=owner_headers,
    )

    assert remove_response.status_code == 204

    list_response = client.get(
        f"/projects/{project_id}/issues/{issue_id}/labels",
        headers=owner_headers,
    )

    assert list_response.status_code == 200
    assert list_response.json() == []


def test_invalid_label_color_returns_422(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="LAB9")
    project_id = project_response.json()["id"]

    response = client.post(
        f"/projects/{project_id}/labels",
        json={
            "name": "backend",
            "color": "red",
        },
        headers=owner_headers,
    )

    assert response.status_code == 422


def test_invalid_label_color_returns_standardized_validation_error(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="ERR1")
    project_id = project_response.json()["id"]

    response = client.post(
        f"/projects/{project_id}/labels",
        json={
            "name": "backend",
            "color": "red",
        },
        headers=owner_headers,
    )

    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "validation_error"
    assert "color" in data["detail"]


def test_project_not_found_returns_standardized_http_error(client):
    create_user(client, "user@example.com", "user", "UserPass1!")
    headers = get_auth_headers(client, "user", "UserPass1!")

    response = client.get("/projects/9999", headers=headers)

    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "http_error"
    assert data["detail"] == "Project not found"