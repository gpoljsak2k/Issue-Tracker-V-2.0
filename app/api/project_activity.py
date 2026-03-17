from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, or_, case, func, delete
from sqlalchemy.orm import Session, selectinload


from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.project import Project
from app.models.user import User
from app.core.permissions import get_project_membership_or_403
from app.models.activity_log import ActivityLog
from app.schemas.activity_log import ActivityLogResponse


router = APIRouter(prefix="/projects", tags=["project_activity"])

@router.get("/{project_id}/activity", response_model=list[ActivityLogResponse])
def list_project_activity(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.scalar(select(Project).where(Project.id == project_id))
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    get_project_membership_or_403(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )

    logs = db.scalars(
        select(ActivityLog)
        .options(selectinload(ActivityLog.actor))
        .where(ActivityLog.project_id == project_id)
        .order_by(ActivityLog.created_at.desc())
    ).all()

    return logs