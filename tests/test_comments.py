from tests.utils import (
    add_project_member,
    create_project,
    create_user,
    get_auth_headers,
)


def setup_project_with_issue(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    create_user(client, "member@example.com", "member", "MemberPass1!")
    create_user(client, "other@example.com", "other", "OtherPass1!")

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")
    member_headers = get_auth_headers(client, "member", "MemberPass1!")
    other_headers = get_auth_headers(client, "other", "OtherPass1!")

    project_response = create_project(client, owner_headers, key="COM1")
    project_id = project_response.json()["id"]

    add_project_member(client, project_id, "member", "member", owner_headers)
    add_project_member(client, project_id, "other", "member", owner_headers)

    issue_response = client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Comment test issue",
            "description": "Used for comment tests",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 2,
        },
        headers=owner_headers,
    )
    issue_id = issue_response.json()["id"]

    return project_id, issue_id, owner_headers, member_headers, other_headers


def test_member_can_create_comment(client):
    project_id, issue_id, owner_headers, member_headers, _ = setup_project_with_issue(client)

    response = client.post(
        f"/projects/{project_id}/issues/{issue_id}/comments",
        json={"body": "I am working on this issue now."},
        headers=member_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["issue_id"] == issue_id
    assert data["author_id"] == 2
    assert data["body"] == "I am working on this issue now."


def test_viewer_cannot_create_comment(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    create_user(client, "viewer@example.com", "viewer", "ViewerPass1!")

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")
    viewer_headers = get_auth_headers(client, "viewer", "ViewerPass1!")

    project_response = create_project(client, owner_headers, key="COM2")
    project_id = project_response.json()["id"]

    add_project_member(client, project_id, "viewer", "viewer", owner_headers)

    issue_response = client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Viewer comment test issue",
            "description": "Viewer should not comment",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )
    issue_id = issue_response.json()["id"]

    response = client.post(
        f"/projects/{project_id}/issues/{issue_id}/comments",
        json={"body": "Viewer comment"},
        headers=viewer_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions for this action"


def test_member_cannot_update_other_users_comment(client):
    project_id, issue_id, owner_headers, member_headers, other_headers = setup_project_with_issue(client)

    comment_response = client.post(
        f"/projects/{project_id}/issues/{issue_id}/comments",
        json={"body": "Original member comment"},
        headers=member_headers,
    )
    comment_id = comment_response.json()["id"]

    response = client.patch(
        f"/projects/{project_id}/issues/{issue_id}/comments/{comment_id}",
        json={"body": "Unauthorized edit"},
        headers=other_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions to update this comment"


def test_owner_can_update_other_users_comment(client):
    project_id, issue_id, owner_headers, member_headers, _ = setup_project_with_issue(client)

    comment_response = client.post(
        f"/projects/{project_id}/issues/{issue_id}/comments",
        json={"body": "Original member comment"},
        headers=member_headers,
    )
    comment_id = comment_response.json()["id"]

    response = client.patch(
        f"/projects/{project_id}/issues/{issue_id}/comments/{comment_id}",
        json={"body": "Owner edited comment"},
        headers=owner_headers,
    )

    assert response.status_code == 200
    assert response.json()["body"] == "Owner edited comment"


def test_comment_author_can_delete_comment(client):
    project_id, issue_id, _, member_headers, _ = setup_project_with_issue(client)

    comment_response = client.post(
        f"/projects/{project_id}/issues/{issue_id}/comments",
        json={"body": "Comment to delete"},
        headers=member_headers,
    )
    comment_id = comment_response.json()["id"]

    response = client.delete(
        f"/projects/{project_id}/issues/{issue_id}/comments/{comment_id}",
        headers=member_headers,
    )

    assert response.status_code == 204