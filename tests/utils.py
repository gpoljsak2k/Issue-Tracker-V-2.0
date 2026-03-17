def create_user(client, email, username, password):
    return client.post(
        "/users/",
        json={
            "email": email,
            "username": username,
            "password": password,
        },
    )


def login_user(client, username, password):
    return client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password,
        },
    )


def get_auth_headers(client, username, password):
    response = login_user(client, username, password)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_project(
    client,
    headers,
    name="Issue Tracker Backend",
    key="ITB",
    description="Backend API project",
):
    return client.post(
        "/projects/",
        json={
            "name": name,
            "key": key,
            "description": description,
        },
        headers=headers,
    )


def add_project_member(client, project_id, username, role, headers):
    return client.post(
        f"/projects/{project_id}/members",
        json={
            "username": username,
            "role": role,
        },
        headers=headers,
    )