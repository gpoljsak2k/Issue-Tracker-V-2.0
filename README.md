# Issue Tracker API

![CI](https://github.com/gpoljsak2k/issue-tracker-api/actions/workflows/ci.yml/badge.svg)

Backend API for a lightweight issue tracking system similar to a simplified Jira.
Built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and **Docker**, with authentication, permissions, filtering, and CI.

---

# Features

## Authentication

* JWT authentication
* Secure password hashing
* Protected endpoints
* Login rate limiting to prevent brute-force attacks

## Projects

* Create projects
* List projects where the user is a member
* Get project details 
* Delete project (owner only)
* Role-based permissions:

  * `owner`
  * `admin`
  * `member`
  * `viewer`

## Project Members

* Add members to a project
* Update member roles
* Remove members from a project
* Owner protection (owner cannot be removed or downgraded)

## Issues

* Create, update and assign issues
* Status workflow (`todo`, `in_progress`, `in_review`, `blocked`, `done`)
* Priority levels (`low`, `medium`, `high`, `urgent`)

## Labels

* Create labels per project
* Update labels
* Delete labels
* Attach labels to issues
* Remove labels from issues
* Many-to-many relationship between issues and labels

## Comments

* Add comments to issues
* Update comments
* Delete comments

## Advanced Issue Listing

* Filtering (`status`, `priority`, `assignee`)
* Search (`title`, `description`)
* Sorting (`created_at`, `priority`, `status`, `title`)
* Pagination with metadata

## Activity Log

Tracks important events such as:

* project created
* issue created
* issue updated
* label created
* label attached to issue
* member role updated

## Security

* JWT authentication
* Role-based access control
* Password hashing
* Login rate limiting
* Protected endpoints

## Quality & Infrastructure

* PostgreSQL database
* Alembic migrations
* Pytest test suite
* Docker development environment
* GitHub Actions CI pipeline

---

# Tech Stack

* **FastAPI**
* **PostgreSQL**
* **SQLAlchemy 2.0**
* **Alembic**
* **Docker**
* **Pytest**
* **GitHub Actions**

---

# Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/issue-tracker-api.git
cd issue-tracker-api
```

Start services:

```bash
docker compose up --build
```

Run database migrations:

```bash
docker compose exec web alembic upgrade head
```

Open API documentation:

```
http://localhost:8000/docs
```

---

# Seed Demo Data

```bash
docker compose exec web python -m scripts.seed_demo
```
**Demo users:**

```
username:	 password:
owner	     OwnerPass1!
admin	     AdminPass1!
member	     MemberPass1!
viewer	     ViewerPass1!
``` 

Demo project key:
- DEMO

# Architecture

The application follows a layered backend structure:

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │---> API routers handle HTTP requests and responses
       ▼
┌─────────────┐
│  FastAPI    │
│   Routers   │
└──────┬──────┘
       │---> Schemas validate input and shape output
       ▼
┌─────────────┐
│ Validation  │
│ Permissions │
└──────┬──────┘
       │---> Permissions enforce role-based access control
       ▼
┌─────────────┐
│  Services   │
└──────┬──────┘
       │---> Services contain reusable business logic
       ▼
┌─────────────┐
│ SQLAlchemy  │
│    ORM      │
└──────┬──────┘
       │---> SQLAlchemy models map application objects to the database
       ▼
┌─────────────┐
│ PostgreSQL  │---> PostgreSQL stores all persistent data
└─────────────┘
```

# API Examples

## Create Project

### Request

```bash
curl -X POST "http://localhost:8000/projects/" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Issue Tracker Demo",
    "key": "DEMO",
    "description": "Demo project with seeded data"
  }'
```
### Response

```bash
{
  "id": 1,
  "name": "Issue Tracker Demo",
  "key": "DEMO",
  "description": "Demo project with seeded data",
  "owner_id": 1
}
```
## Create Issue

### Request

```bash
curl -X POST "http://localhost:8000/projects/1/issues" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement JWT login",
    "description": "Add authentication and protected routes",
    "status": "todo",
    "priority": "high",
    "assignee_id": 2
  }'
```
### Response

```bash
{
  "id": 1,
  "title": "Implement JWT login",
  "description": "Add authentication and protected routes",
  "status": "todo",
  "priority": "high",
  "project_id": 1,
  "reporter_id": 1,
  "assignee_id": 2,
  "created_at": "2026-03-12T10:00:00Z",
  "updated_at": "2026-03-12T10:00:00Z"
}
```
## List Issues with Filtering, Search and Pagination

### Request

```bash
curl "http://localhost:8000/projects/1/issues?status=todo&search=jwt&sort_by=priority&order=desc&limit=20&offset=0" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```
### Response

```bash
{
  "items": [
    {
      "id": 1,
      "title": "Implement JWT login",
      "description": "Add authentication and protected routes",
      "status": "todo",
      "priority": "high",
      "project_id": 1,
      "reporter_id": 1,
      "assignee_id": 2,
      "created_at": "2026-03-12T10:00:00Z",
      "updated_at": "2026-03-12T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

# Running Tests

```bash
pytest
```

Tests also run automatically in **GitHub Actions CI** on every push and pull request.

---

# Database

Main entities:

* **users**
* **projects**
* **project_members**
* **issues**
* **labels**
* **issue_labels**
* **comments**
* **activity_logs**

Relationships overview:

```
User ──< ProjectMember >── Project
Project ──< Issues
Project ──< Labels
Issue ──< IssueLabels >── Label
Issue ──< Comments
```

---

# Project Structure

```
app
├── api        # API endpoints
├── core       # config and security
├── db         # database session
├── models     # SQLAlchemy models
├── schemas    # Pydantic schemas
└── services   # business logic

scripts        # utility scripts (demo data)
tests          # pytest test suite
alembic        # database migrations
docker         # postgres initialization
.github        # CI workflows
```

---

# Possible Improvements

* Label filtering for issues
* Project dashboard statistics
* Full-text search using PostgreSQL
* WebSocket notifications
* Email notifications
* User invitations via email

---

# License

This project is intended as a **learning and portfolio project**.
