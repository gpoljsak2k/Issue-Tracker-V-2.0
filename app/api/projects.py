from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, or_, case, func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse
from app.schemas.project_member import ProjectMemberResponse, ProjectMemberCreate
from app.core.permissions import get_project_membership_or_403, require_project_role, can_manage_comment, require_project_write_access
from app.models.issue import Issue
from app.schemas.issue import IssueCreate, IssueResponse, IssueUpdate, PaginatedIssueResponse
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.services.activity_service import create_activity_log
from app.models.activity_log import ActivityLog
from app.schemas.activity_log import ActivityLogResponse
from typing import Literal
from app.models.label import Label
from app.models.issue_label import IssueLabel
from app.schemas.label import LabelCreate, LabelResponse, IssueLabelAttach, LabelUpdate
from app.schemas.project_member import ProjectMemberResponse, ProjectMemberCreate, ProjectMemberUpdate


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
        .where(ActivityLog.project_id == project_id)
        .order_by(ActivityLog.created_at.desc())
    ).all()

    return logs

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

    user_to_add = db.scalar(select(User).where(User.id == member_in.user_id))
    if user_to_add is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    existing_membership = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == member_in.user_id,
        )
    )
    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this project",
        )

    membership = ProjectMember(
        project_id=project_id,
        user_id=member_in.user_id,
        role=member_in.role,
    )

    db.add(membership)
    create_activity_log(
        db,
        project_id=project_id,
        actor_id=current_user.id,
        action="member_added",
        metadata_json={
            "added_user_id": member_in.user_id,
            "role": member_in.role,
        },
    )
    db.commit()
    db.refresh(membership)
    return membership

@router.get("/{project_id}/members", response_model=list[ProjectMemberResponse])
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
        select(ProjectMember).where(ProjectMember.project_id == project_id)
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
            detail="Owner cannot be removed from the project",
        )

    create_activity_log(
        db,
        project_id=project_id,
        actor_id=current_user.id,
        action="member_removed",
        metadata_json={
            "removed_user_id": user_id,
            "old_role": target_membership.role,
        },
    )

    db.delete(target_membership)
    db.commit()

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

@router.post(
    "/{project_id}/issues/{issue_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    project_id: int,
    issue_id: int,
    comment_in: CommentCreate,
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

    comment = Comment(
        issue_id=issue.id,
        author_id=current_user.id,
        body=comment_in.body,
    )

    db.add(comment)
    db.flush()

    create_activity_log(
        db,
        project_id=project_id,
        issue_id=issue.id,
        actor_id=current_user.id,
        action="comment_added",
        metadata_json={
            "comment_id": comment.id,
        },
    )

    db.commit()
    db.refresh(comment)
    return comment

@router.get(
    "/{project_id}/issues/{issue_id}/comments",
    response_model=list[CommentResponse],
)
def list_issue_comments(
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

    get_project_membership_or_403(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )

    comments = db.scalars(
        select(Comment).where(Comment.issue_id == issue_id).order_by(Comment.created_at)
    ).all()

    return comments

@router.patch(
    "/{project_id}/issues/{issue_id}/comments/{comment_id}",
    response_model=CommentResponse,
)
def update_comment(
    project_id: int,
    issue_id: int,
    comment_id: int,
    comment_in: CommentUpdate,
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

    comment = db.scalar(
        select(Comment).where(
            Comment.id == comment_id,
            Comment.issue_id == issue_id,
        )
    )
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    membership = get_project_membership_or_403(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )
    require_project_write_access(membership)

    if not can_manage_comment(
        comment_author_id=comment.author_id,
        current_user_id=current_user.id,
        project_membership=membership,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this comment",
        )

    old_body = comment.body
    comment.body = comment_in.body

    create_activity_log(
        db,
        project_id=project_id,
        issue_id=issue_id,
        actor_id=current_user.id,
        action="comment_updated",
        metadata_json={
            "comment_id": comment.id,
            "old_body": old_body,
            "new_body": comment.body,
        },
    )

    db.commit()
    db.refresh(comment)
    return comment

@router.delete(
    "/{project_id}/issues/{issue_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    project_id: int,
    issue_id: int,
    comment_id: int,
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

    comment = db.scalar(
        select(Comment).where(
            Comment.id == comment_id,
            Comment.issue_id == issue_id,
        )
    )
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    membership = get_project_membership_or_403(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )
    require_project_write_access(membership)

    if not can_manage_comment(
        comment_author_id=comment.author_id,
        current_user_id=current_user.id,
        project_membership=membership,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this comment",
        )

    create_activity_log(
        db,
        project_id=project_id,
        issue_id=issue_id,
        actor_id=current_user.id,
        action="comment_deleted",
        metadata_json={
            "comment_id": comment.id,
        },
    )

    db.delete(comment)
    db.commit()

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

@router.post(
    "/{project_id}/labels",
    response_model=LabelResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_label(
    project_id: int,
    label_in: LabelCreate,
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

    existing_label = db.scalar(
        select(Label).where(
            Label.project_id == project_id,
            Label.name == label_in.name,
        )
    )
    if existing_label is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Label name already exists in this project",
        )

    label = Label(
        project_id=project_id,
        name=label_in.name,
        color=label_in.color,
    )

    db.add(label)
    db.flush()

    create_activity_log(
        db,
        project_id=project_id,
        actor_id=current_user.id,
        action="label_created",
        metadata_json={
            "label_id": label.id,
            "name": label.name,
            "color": label.color,
        },
    )

    db.commit()
    db.refresh(label)
    return label

@router.get("/{project_id}/labels", response_model=list[LabelResponse])
def list_project_labels(
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

    labels = db.scalars(
        select(Label)
        .where(Label.project_id == project_id)
        .order_by(Label.name.asc())
    ).all()

    return labels

@router.patch(
    "/{project_id}/labels/{label_id}",
    response_model=LabelResponse,
)
def update_label(
    project_id: int,
    label_id: int,
    label_in: LabelUpdate,
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

    label = db.scalar(
        select(Label).where(
            Label.id == label_id,
            Label.project_id == project_id,
        )
    )
    if label is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Label not found",
        )

    update_data = label_in.model_dump(exclude_unset=True)

    if "name" in update_data:
        existing_label = db.scalar(
            select(Label).where(
                Label.project_id == project_id,
                Label.name == update_data["name"],
                Label.id != label_id,
            )
        )
        if existing_label is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Label name already exists in this project",
            )

    changes = {}
    for field, new_value in update_data.items():
        old_value = getattr(label, field)
        if old_value != new_value:
            changes[field] = {"old": old_value, "new": new_value}
            setattr(label, field, new_value)

    if changes:
        create_activity_log(
            db,
            project_id=project_id,
            actor_id=current_user.id,
            action="label_updated",
            metadata_json={
                "label_id": label.id,
                "changes": changes,
            },
        )

    db.commit()
    db.refresh(label)
    return label

@router.delete(
    "/{project_id}/labels/{label_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_label(
    project_id: int,
    label_id: int,
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

    label = db.scalar(
        select(Label).where(
            Label.id == label_id,
            Label.project_id == project_id,
        )
    )
    if label is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Label not found",
        )

    create_activity_log(
        db,
        project_id=project_id,
        actor_id=current_user.id,
        action="label_deleted",
        metadata_json={
            "label_id": label.id,
            "name": label.name,
        },
    )

    issue_labels = db.scalars(
        select(IssueLabel).where(IssueLabel.label_id == label.id)
    ).all()

    for issue_label in issue_labels:
        db.delete(issue_label)

    db.delete(label)
    db.commit()

@router.post(
    "/{project_id}/issues/{issue_id}/labels",
    status_code=status.HTTP_201_CREATED,
)
def attach_label_to_issue(
    project_id: int,
    issue_id: int,
    label_in: IssueLabelAttach,
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

    label = db.scalar(
        select(Label).where(
            Label.id == label_in.label_id,
            Label.project_id == project_id,
        )
    )
    if label is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Label not found",
        )

    existing_issue_label = db.scalar(
        select(IssueLabel).where(
            IssueLabel.issue_id == issue_id,
            IssueLabel.label_id == label_in.label_id,
        )
    )
    if existing_issue_label is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Label is already attached to this issue",
        )

    issue_label = IssueLabel(
        issue_id=issue_id,
        label_id=label_in.label_id,
    )

    db.add(issue_label)

    create_activity_log(
        db,
        project_id=project_id,
        issue_id=issue_id,
        actor_id=current_user.id,
        action="label_attached_to_issue",
        metadata_json={
            "label_id": label.id,
            "label_name": label.name,
        },
    )

    db.commit()

    return {"message": "Label attached successfully"}

@router.get("/{project_id}/issues/{issue_id}/labels", response_model=list[LabelResponse])
def list_issue_labels(
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

    get_project_membership_or_403(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )

    labels = db.scalars(
        select(Label)
        .join(IssueLabel, IssueLabel.label_id == Label.id)
        .where(IssueLabel.issue_id == issue_id)
        .order_by(Label.name.asc())
    ).all()

    return labels

@router.delete(
    "/{project_id}/issues/{issue_id}/labels/{label_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_label_from_issue(
    project_id: int,
    issue_id: int,
    label_id: int,
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

    label = db.scalar(
        select(Label).where(
            Label.id == label_id,
            Label.project_id == project_id,
        )
    )
    if label is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Label not found",
        )

    issue_label = db.scalar(
        select(IssueLabel).where(
            IssueLabel.issue_id == issue_id,
            IssueLabel.label_id == label_id,
        )
    )
    if issue_label is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Label is not attached to this issue",
        )

    create_activity_log(
        db,
        project_id=project_id,
        issue_id=issue_id,
        actor_id=current_user.id,
        action="label_removed_from_issue",
        metadata_json={
            "label_id": label.id,
            "label_name": label.name,
        },
    )

    db.delete(issue_label)
    db.commit()




