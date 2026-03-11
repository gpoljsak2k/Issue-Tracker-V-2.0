# Issue Tracker API

FastAPI backend for an issue tracking system similar to a simplified Jira.

## Features

- User authentication (JWT)
- Project management
- Role-based permissions (owner, admin, member, viewer)
- Issue tracking
- Comments on issues
- Activity log
- PostgreSQL database
- Alembic migrations
- Docker setup
- Pytest test suite
- GitHub Actions CI

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker
- Pytest
- GitHub Actions

## Run locally

Start services:

```bash
docker compose up --build