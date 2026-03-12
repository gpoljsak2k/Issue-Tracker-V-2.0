from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.permissions import get_project_membership_or_403, require_project_role, require_project_write_access
from app.db.session import get_db
from app.models.issue import Issue
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.schemas.issue import IssueCreate, IssueResponse, IssueUpdate, PaginatedIssueResponse

from app.services.activity_service import create_activity_log

router = APIRouter(prefix="/projects", tags=["issues"])

@router.post(
    "/{project_id}/issues",
    response_model=IssueResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_issue(
    project_id: int,
    issue_in: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.scalar(select(Project).where(Project.id == project_id))
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
    require_project_write_access(membership)

    if issue_in.assignee_id is not None:
        assignee_membership = db.scalar(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == issue_in.assignee_id,
            )
        )
        if assignee_membership is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee must be a member of the project",
            )

    issue = Issue(
        title=issue_in.title,
        description=issue_in.description,
        status=issue_in.status,
        priority=issue_in.priority,
        project_id=project_id,
        reporter_id=current_user.id,
        assignee_id=issue_in.assignee_id,
    )

    db.add(issue)
    db.flush()

    create_activity_log(
        db,
        project_id=project_id,
        issue_id=issue.id,
        actor_id=current_user.id,
        action="issue_created",
        metadata_json={
            "title": issue.title,
            "status": issue.status,
            "priority": issue.priority,
            "assignee_id": issue.assignee_id,
        },
    )

    db.commit()
    db.refresh(issue)
    return issue

@router.get("/{project_id}/issues", response_model=PaginatedIssueResponse)
def list_project_issues(
    project_id: int,
    status_filter: Literal["todo", "in_progress", "in_review", "done", "blocked"] | None = Query(
        default=None,
        alias="status",
    ),
    priority: Literal["low", "medium", "high", "urgent"] | None = Query(default=None),
    assignee_id: int | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1, max_length=100),
    sort_by: Literal["created_at", "updated_at", "priority", "status", "title"] = Query(
        default="created_at"
    ),
    order: Literal["asc", "desc"] = Query(default="desc"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
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

    base_query = select(Issue).where(Issue.project_id == project_id)

    if status_filter is not None:
        base_query = base_query.where(Issue.status == status_filter)

    if priority is not None:
        base_query = base_query.where(Issue.priority == priority)

    if assignee_id is not None:
        base_query = base_query.where(Issue.assignee_id == assignee_id)

    if search is not None:
        search_term = f"%{search}%"
        base_query = base_query.where(
            or_(
                Issue.title.ilike(search_term),
                Issue.description.ilike(search_term),
            )
        )

    total = db.scalar(
        select(func.count()).select_from(base_query.subquery())
    )

    priority_order = case(
        (Issue.priority == "low", 1),
        (Issue.priority == "medium", 2),
        (Issue.priority == "high", 3),
        (Issue.priority == "urgent", 4),
        else_=999,
    )

    status_order = case(
        (Issue.status == "todo", 1),
        (Issue.status == "in_progress", 2),
        (Issue.status == "in_review", 3),
        (Issue.status == "blocked", 4),
        (Issue.status == "done", 5),
        else_=999,
    )

    sort_column_map = {
        "created_at": Issue.created_at,
        "updated_at": Issue.updated_at,
        "priority": priority_order,
        "status": status_order,
        "title": Issue.title,
    }
    sort_column = sort_column_map[sort_by]

    query = base_query

    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    query = query.limit(limit).offset(offset)

    issues = db.scalars(query).all()

    return {
        "items": issues,
        "total": total,
        "limit": limit,
        "offset": offset,
    }

@router.patch(
    "/{project_id}/issues/{issue_id}",
    response_model=IssueResponse,
)
def update_issue(
    project_id: int,
    issue_id: int,
    issue_in: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = db.scalar(
        select(Issue).where(
            Issue.id == issue_id,
            Issue.project_id == project_id,
        )
    )

    if issue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )

    membership = get_project_membership_or_403(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )
    require_project_write_access(membership)

    if issue_in.assignee_id is not None:
        assignee_membership = db.scalar(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == issue_in.assignee_id,
            )
        )
        if assignee_membership is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee must be a member of the project",
            )

    update_data = issue_in.model_dump(exclude_unset=True)

    changes = {}
    for field, new_value in update_data.items():
        old_value = getattr(issue, field)
        if old_value != new_value:
            changes[field] = {
                "old": old_value,
                "new": new_value,
            }
            setattr(issue, field, new_value)

    if changes:
        create_activity_log(
            db,
            project_id=project_id,
            issue_id=issue.id,
            actor_id=current_user.id,
            action="issue_updated",
            metadata_json={"changes": changes},
        )

    db.commit()
    db.refresh(issue)

    return issue

@router.delete(
    "/{project_id}/issues/{issue_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_issue(
    project_id: int,
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = db.scalar(
        select(Issue).where(
            Issue.id == issue_id,
            Issue.project_id == project_id,
        )
    )
    if issue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )

    membership = get_project_membership_or_403(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )
    require_project_role(membership, {"owner", "admin"})

    create_activity_log(
        db,
        project_id=project_id,
        issue_id=issue.id,
        actor_id=current_user.id,
        action="issue_deleted",
        metadata_json={
            "issue_id": issue.id,
            "title": issue.title,
        },
    )

    db.delete(issue)
    db.commit()
