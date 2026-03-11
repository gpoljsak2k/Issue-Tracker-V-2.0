from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project_member import ProjectMember


def get_project_membership_or_403(
    db: Session,
    project_id: int,
    user_id: int,
) -> ProjectMember:
    membership = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions for this project",
        )

    return membership


def require_project_role(
    membership: ProjectMember,
    allowed_roles: set[str],
) -> None:
    if membership.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions for this action",
        )

def can_manage_comment(
    *,
    comment_author_id: int,
    current_user_id: int,
    project_membership: ProjectMember,
) -> bool:
    if comment_author_id == current_user_id:
        return True

    return project_membership.role in {"owner", "admin"}

def require_project_write_access(membership: ProjectMember) -> None:
    if membership.role not in {"owner", "admin", "member"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions for this action",
        )