from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.permissions import get_project_membership_or_403, require_project_write_access
from app.db.session import get_db

from app.models.project import Project
from app.models.issue import Issue
from app.models.label import Label
from app.models.issue_label import IssueLabel
from app.models.user import User

from app.schemas.label import LabelCreate, LabelResponse, LabelUpdate, IssueLabelAttach

from app.services.activity_service import create_activity_log


router = APIRouter(prefix="/projects", tags=["labels"])

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