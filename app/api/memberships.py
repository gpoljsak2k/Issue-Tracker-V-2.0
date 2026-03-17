from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.core.permissions import (
    get_project_membership_or_403,
    require_project_role,
)
from app.db.session import get_db
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.services.activity_service import create_activity_log
from app.schemas.project_member import (
    ProjectMemberResponse,
    ProjectMemberCreate,
    ProjectMemberUpdate,
)

router = APIRouter(prefix="/projects", tags=["members"])


@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_project_member(
    project_id: int,
    member_in: ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_membership = get_project_membership_or_403(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )
    require_project_role(current_membership, {"owner", "admin"})

    project = db.scalar(select(Project).where(Project.id == project_id))
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    user_to_add = db.scalar(
        select(User).where(User.username == member_in.username)
    )
    if user_to_add is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    existing_membership = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_to_add.id,
        )
    )
    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this project",
        )

    membership = ProjectMember(
        project_id=project_id,
        user_id=user_to_add.id,
        role=member_in.role,
    )

    db.add(membership)
    db.flush()

    create_activity_log(
        db,
        project_id=project_id,
        actor_id=current_user.id,
        action="member_added",
        metadata_json={
            "added_user_id": user_to_add.id,
            "added_username": user_to_add.username,
            "role": member_in.role,
            "author_username": current_user.username,
        },
    )

    db.commit()
    db.refresh(membership)
    return membership


@router.get(
    "/{project_id}/members",
    response_model=list[ProjectMemberResponse],
)
def list_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_project_membership_or_403(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )

    members = db.scalars(
        select(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .where(ProjectMember.project_id == project_id)
    ).all()

    return members


@router.patch(
    "/{project_id}/members/{user_id}",
    response_model=ProjectMemberResponse,
)
def update_project_member_role(
    project_id: int,
    user_id: int,
    member_in: ProjectMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.scalar(select(Project).where(Project.id == project_id))
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    current_membership = get_project_membership_or_403(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )
    require_project_role(current_membership, {"owner", "admin"})

    target_membership = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    if target_membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found",
        )

    if target_membership.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner role cannot be changed",
        )

    old_role = target_membership.role
    new_role = member_in.role

    if old_role != new_role:
        target_membership.role = new_role

        create_activity_log(
            db,
            project_id=project_id,
            actor_id=current_user.id,
            action="member_role_updated",
            metadata_json={
                "target_user_id": user_id,
                "target_username": target_membership.user.username,
                "old_role": old_role,
                "new_role": new_role,
            },
        )

    db.commit()
    db.refresh(target_membership)
    return target_membership


@router.delete(
    "/{project_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_project_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.scalar(select(Project).where(Project.id == project_id))
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    current_membership = get_project_membership_or_403(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )
    require_project_role(current_membership, {"owner", "admin"})

    target_membership = db.scalar(
        select(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    if target_membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found",
        )

    if target_membership.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner cannot be removed from the project",
        )

    create_activity_log(
        db,
        project_id=project_id,
        actor_id=current_user.id,
        action="member_removed",
        metadata_json={
            "target_user_id": target_membership.user_id,
            "target_username": target_membership.user.username,
            "removed_user_id": target_membership.user_id,
            "old_role": target_membership.role,
        },
    )

    db.delete(target_membership)
    db.commit()