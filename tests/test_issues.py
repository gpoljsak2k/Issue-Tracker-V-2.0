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


def test_member_cannot_delete_issue(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    create_user(client, "member@example.com", "member", "MemberPass1!")

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")
    member_headers = get_auth_headers(client, "member", "MemberPass1!")

    project_response = create_project(client, owner_headers, key="ISS4")
    project_id = project_response.json()["id"]

    add_project_member(client, project_id, 2, "member", owner_headers)

    issue_response = client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Delete permission test",
            "description": "Only admin or owner may delete",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 2,
        },
        headers=owner_headers,
    )
    issue_id = issue_response.json()["id"]

    response = client.delete(
        f"/projects/{project_id}/issues/{issue_id}",
        headers=member_headers,
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


def test_list_issues_can_filter_by_status(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="FIL1")
    project_id = project_response.json()["id"]

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Todo issue",
            "description": "First issue",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Done issue",
            "description": "Second issue",
            "status": "done",
            "priority": "high",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    response = client.get(
        f"/projects/{project_id}/issues?status=todo",
        headers=owner_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["offset"] == 0
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Todo issue"
    assert data["items"][0]["status"] == "todo"


def test_list_issues_can_filter_by_priority(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="FIL2")
    project_id = project_response.json()["id"]

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Low priority issue",
            "description": "First issue",
            "status": "todo",
            "priority": "low",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Urgent priority issue",
            "description": "Second issue",
            "status": "todo",
            "priority": "urgent",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    response = client.get(
        f"/projects/{project_id}/issues?priority=urgent",
        headers=owner_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Urgent priority issue"
    assert data["items"][0]["priority"] == "urgent"


def test_list_issues_can_filter_by_assignee(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    create_user(client, "member@example.com", "member", "MemberPass1!")

    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="FIL3")
    project_id = project_response.json()["id"]

    add_project_member(client, project_id, 2, "member", owner_headers)

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Assigned to owner",
            "description": "Owner issue",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Assigned to member",
            "description": "Member issue",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 2,
        },
        headers=owner_headers,
    )

    response = client.get(
        f"/projects/{project_id}/issues?assignee_id=2",
        headers=owner_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Assigned to member"
    assert data["items"][0]["assignee_id"] == 2


def test_list_issues_supports_limit_and_offset(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="FIL4")
    project_id = project_response.json()["id"]

    for i in range(3):
        client.post(
            f"/projects/{project_id}/issues",
            json={
                "title": f"Issue {i}",
                "description": f"Issue number {i}",
                "status": "todo",
                "priority": "medium",
                "assignee_id": 1,
            },
            headers=owner_headers,
        )

    response = client.get(
        f"/projects/{project_id}/issues?limit=2&offset=0",
        headers=owner_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert len(data["items"]) == 2


def test_list_issues_rejects_invalid_limit(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="FIL5")
    project_id = project_response.json()["id"]

    response = client.get(
        f"/projects/{project_id}/issues?limit=0",
        headers=owner_headers,
    )

    assert response.status_code == 422


def test_list_issues_can_search_by_title_and_description(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="SRCH1")
    project_id = project_response.json()["id"]

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Implement JWT authentication",
            "description": "Add login and access token support",
            "status": "todo",
            "priority": "high",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Fix pagination bug",
            "description": "Limit and offset are broken",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    response = client.get(
        f"/projects/{project_id}/issues?search=jwt",
        headers=owner_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Implement JWT authentication"


def test_list_issues_can_sort_by_title_ascending(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="SORT1")
    project_id = project_response.json()["id"]

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Zeta issue",
            "description": "Last alphabetically",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Alpha issue",
            "description": "First alphabetically",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    response = client.get(
        f"/projects/{project_id}/issues?sort_by=title&order=asc",
        headers=owner_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["items"][0]["title"] == "Alpha issue"
    assert data["items"][1]["title"] == "Zeta issue"


def test_list_issues_can_sort_by_title_descending(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="SORT2")
    project_id = project_response.json()["id"]

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Alpha issue",
            "description": "First alphabetically",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Zeta issue",
            "description": "Last alphabetically",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    response = client.get(
        f"/projects/{project_id}/issues?sort_by=title&order=desc",
        headers=owner_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["items"][0]["title"] == "Zeta issue"
    assert data["items"][1]["title"] == "Alpha issue"


def test_list_issues_can_combine_search_and_filters(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="SRCH2")
    project_id = project_response.json()["id"]

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Implement JWT login",
            "description": "Authentication work",
            "status": "todo",
            "priority": "high",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Implement JWT refresh token",
            "description": "Token lifecycle work",
            "status": "done",
            "priority": "high",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    response = client.get(
        f"/projects/{project_id}/issues?search=jwt&status=todo",
        headers=owner_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Implement JWT login"
    assert data["items"][0]["status"] == "todo"


def test_list_issues_rejects_invalid_sort_by(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="SORT3")
    project_id = project_response.json()["id"]

    response = client.get(
        f"/projects/{project_id}/issues?sort_by=invalid_field",
        headers=owner_headers,
    )

    assert response.status_code == 422


def test_list_issues_sorts_priority_by_business_order_desc(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="BIZ1")
    project_id = project_response.json()["id"]

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Low issue",
            "description": "Low priority",
            "status": "todo",
            "priority": "low",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Urgent issue",
            "description": "Urgent priority",
            "status": "todo",
            "priority": "urgent",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "High issue",
            "description": "High priority",
            "status": "todo",
            "priority": "high",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    response = client.get(
        f"/projects/{project_id}/issues?sort_by=priority&order=desc",
        headers=owner_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["items"][0]["priority"] == "urgent"
    assert data["items"][1]["priority"] == "high"
    assert data["items"][2]["priority"] == "low"


def test_list_issues_sorts_status_by_business_order_asc(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="BIZ2")
    project_id = project_response.json()["id"]

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Done issue",
            "description": "Completed work",
            "status": "done",
            "priority": "medium",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "Todo issue",
            "description": "Not started",
            "status": "todo",
            "priority": "medium",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    client.post(
        f"/projects/{project_id}/issues",
        json={
            "title": "In progress issue",
            "description": "Currently active",
            "status": "in_progress",
            "priority": "medium",
            "assignee_id": 1,
        },
        headers=owner_headers,
    )

    response = client.get(
        f"/projects/{project_id}/issues?sort_by=status&order=asc",
        headers=owner_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["items"][0]["status"] == "todo"
    assert data["items"][1]["status"] == "in_progress"
    assert data["items"][2]["status"] == "done"


def test_list_issues_returns_pagination_metadata(client):
    create_user(client, "owner@example.com", "owner", "OwnerPass1!")
    owner_headers = get_auth_headers(client, "owner", "OwnerPass1!")

    project_response = create_project(client, owner_headers, key="PAGE1")
    project_id = project_response.json()["id"]

    for i in range(3):
        client.post(
            f"/projects/{project_id}/issues",
            json={
                "title": f"Issue {i}",
                "description": f"Description {i}",
                "status": "todo",
                "priority": "medium",
                "assignee_id": 1,
            },
            headers=owner_headers,
        )

    response = client.get(
        f"/projects/{project_id}/issues?limit=2&offset=1",
        headers=owner_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["limit"] == 2
    assert data["offset"] == 1
    assert len(data["items"]) == 2