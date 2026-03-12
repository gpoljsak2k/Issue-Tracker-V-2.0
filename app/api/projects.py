from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, or_, case, func, delete
from sqlalchemy.orm import Session


from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse
from app.core.permissions import get_project_membership_or_403
from app.models.activity_log import ActivityLog
from app.schemas.activity_log import ActivityLogResponse
from app.models.issue import Issue
from app.models.comment import Comment
from app.models.label import Label
from app.models.issue_label import IssueLabel



router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_project = db.scalar(select(Project).where(Project.key == project_in.key))
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project key already exists",
        )

    project = Project(
        name=project_in.name,
        key=project_in.key,
        description=project_in.description,
        owner_id=current_user.id,
    )

    db.add(project)
    db.flush()

    membership = ProjectMember(
        project_id=project.id,
        user_id=current_user.id,
        role="owner",
    )
    db.add(membership)

    db.commit()
    db.refresh(project)
    return project

@router.get("/", response_model=list[ProjectResponse])
def list_my_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects = db.scalars(
        select(Project)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .where(ProjectMember.user_id == current_user.id)
        .order_by(Project.id.desc())
    ).all()

    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.scalar(
        select(Project).where(Project.id == project_id)
    )

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

    return project

@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.scalar(
        select(Project).where(Project.id == project_id)
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    membership = get_project_membership_or_403(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )

    if membership.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can delete the project",
        )

    issue_ids = db.scalars(
        select(Issue.id).where(Issue.project_id == project_id)
    ).all()

    if issue_ids:
        db.execute(
            delete(Comment).where(Comment.issue_id.in_(issue_ids))
        )
        db.execute(
            delete(IssueLabel).where(IssueLabel.issue_id.in_(issue_ids))
        )

    db.execute(
        delete(ActivityLog).where(ActivityLog.project_id == project_id)
    )
    db.execute(
        delete(ProjectMember).where(ProjectMember.project_id == project_id)
    )
    db.execute(
        delete(Issue).where(Issue.project_id == project_id)
    )
    db.execute(
        delete(Label).where(Label.project_id == project_id)
    )
    db.execute(
        delete(Project).where(Project.id == project_id)
    )

    db.commit()







