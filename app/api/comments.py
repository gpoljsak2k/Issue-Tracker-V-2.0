from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.core.permissions import (
    can_manage_comment,
    get_project_membership_or_403,
    require_project_write_access,
)
from app.db.session import get_db
from app.models.comment import Comment
from app.models.issue import Issue
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.services.activity_service import create_activity_log


router = APIRouter(prefix="/projects", tags=["comments"])

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
            "body": comment.body,
            "author_username": current_user.username,
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
            "author_username": current_user.username,
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
        select(Comment)
        .options(selectinload(Comment.author))
        .where(
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
            "body": comment.body,
            "author_username": comment.author.username,
        },
    )

    db.delete(comment)
    db.commit()