from typing import Any
from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog


def create_activity_log(
    db: Session,
    *,
    project_id: int,
    actor_id: int,
    action: str,
    issue_id: int | None = None,
    metadata_json: dict[str, Any] | None = None,
) -> ActivityLog:
    log = ActivityLog(
        project_id=project_id,
        issue_id=issue_id,
        actor_id=actor_id,
        action=action,
        metadata_json=metadata_json,
    )
    db.add(log)
    return log