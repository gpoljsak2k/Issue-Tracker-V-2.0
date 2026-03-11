from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
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
from app.schemas.issue import IssueCreate, IssueResponse, IssueUpdate
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.services.activity_service import create_activity_log
from app.models.activity_log import ActivityLog
from app.schemas.activity_log import ActivityLogResponse


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

@router.get("/{project_id}/issues", response_model=list[IssueResponse])
def list_project_issues(
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

    issues = db.scalars(
        select(Issue).where(Issue.project_id == project_id)
    ).all()

    return issues

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