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

## Projects

* Create and manage projects
* Role-based permissions:

  * `owner`
  * `admin`
  * `member`
  * `viewer`

## Issues

* Create, update and assign issues
* Status workflow (`todo`, `in_progress`, `in_review`, `blocked`, `done`)
* Priority levels (`low`, `medium`, `high`, `urgent`)

## Labels

* Create labels per project
* Attach labels to issues
* Many-to-many relationship between issues and labels

## Advanced Issue Listing

* Filtering (`status`, `priority`, `assignee`)
* Search (`title`, `description`)
* Sorting (`created_at`, `priority`, `status`, `title`)
* Pagination with metadata

## Activity Log

Tracks important events such as:

* issue created
* issue updated
* label created
* label attached to issue

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

**username:**	**password:**
owner	    OwnerPass1!
admin	    AdminPass1!
member	    MemberPass1!
viewer	    ViewerPass1!

Demo project key:
- DEMO


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
* Rate limiting
* User invitations via email

---

# License

This project is intended as a **learning and portfolio project**.
