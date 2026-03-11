from tests.utils import (
    add_project_member,
    create_project,
    create_user,
    get_auth_headers,
)


def test_member_can_create_issue(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    create_user(client, "member@example.com", "member", "MemberPass1!")

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")
    member_headers = get_auth_headers(client, "member", "MemberPass1!")

    project_response = create_project(client, owner_headers, key="ISS1")
    project_id = project_response.json()["id"]

    add_project_member(client, project_id, 2, "member", owner_headers)

    response = client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Implement JWT authentication",
            "description": "Add login and protected routes",
            "status": "todo",
            "priority": "high",
            "assignee_id": 2,
        },
        headers=member_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Implement JWT authentication"
    assert data["reporter_id"] == 2
    assert data["assignee_id"] == 2
    assert data["project_id"] == project_id

def test_cannot_assign_issue_to_non_member(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    create_user(client, "member@example.com", "member", "MemberPass1!")
    create_user(client, "outsider@example.com", "outsider", "OutsiderPass1!")

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")
    member_headers = get_auth_headers(client, "member", "MemberPass1!")

    project_response = create_project(client, owner_headers, key="ISS2")
    project_id = project_response.json()["id"]

    add_project_member(client, project_id, 2, "member", owner_headers)

    response = client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Invalid assignment test",
            "description": "Assignee should be project member",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 3,
        },
        headers=member_headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Assignee must be a member of the project"

def test_viewer_cannot_create_issue(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    create_user(client, "viewer@example.com", "viewer", "ViewerPass1!")

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")
    viewer_headers = get_auth_headers(client, "viewer", "ViewerPass1!")

    project_response = create_project(client, owner_headers, key="ISS3")
    project_id = project_response.json()["id"]

    add_project_member(client, project_id, 2, "viewer", owner_headers)

    response = client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Viewer should not create issue",
            "description": "Forbidden action",
            "status": "todo",
            "priority": "medium",
            "assignee_id": None,
        },
        headers=viewer_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions for this action"

def test_owner_can_delete_issue(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="ISS5")
    project_id = project_response.json()["id"]

    issue_response = client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Owner delete test",
            "description": "Owner should be able to delete",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )
    issue_id = issue_response.json()["id"]

    response = client.delete(
        f"/projects/{project_id}/issues/{issue_id}",
        headers=owner_headers,
    )

    assert response.status_code == 204