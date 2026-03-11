from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.issue import Issue
from app.models.label import Label
from app.models.issue_label import IssueLabel


def get_or_create_user(db, *, email: str, username: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user:
        return user

    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_project(db, *, name: str, key: str, description: str | None, owner_id: int) -> Project:
    project = db.scalar(select(Project).where(Project.key == key))
    if project:
        return project

    project = Project(
        name=name,
        key=key,
        description=description,
        owner_id=owner_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_or_create_membership(db, *, project_id: int, user_id: int, role: str) -> ProjectMember:
    membership = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    if membership:
        return membership

    membership = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role=role,
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def get_or_create_label(db, *, project_id: int, name: str, color: str) -> Label:
    label = db.scalar(
        select(Label).where(
            Label.project_id == project_id,
            Label.name == name,
        )
    )
    if label:
        return label

    label = Label(
        project_id=project_id,
        name=name,
        color=color,
    )
    db.add(label)
    db.commit()
    db.refresh(label)
    return label


def get_or_create_issue(
    db,
    *,
    project_id: int,
    title: str,
    description: str,
    status: str,
    priority: str,
    reporter_id: int,
    assignee_id: int | None,
) -> Issue:
    issue = db.scalar(
        select(Issue).where(
            Issue.project_id == project_id,
            Issue.title == title,
        )
    )
    if issue:
        return issue

    issue = Issue(
        project_id=project_id,
        title=title,
        description=description,
        status=status,
        priority=priority,
        reporter_id=reporter_id,
        assignee_id=assignee_id,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


def attach_label_if_missing(db, *, issue_id: int, label_id: int) -> None:
    existing = db.scalar(
        select(IssueLabel).where(
            IssueLabel.issue_id == issue_id,
            IssueLabel.label_id == label_id,
        )
    )
    if existing:
        return

    issue_label = IssueLabel(issue_id=issue_id, label_id=label_id)
    db.add(issue_label)
    db.commit()


def main():
    db = SessionLocal()
    try:
        owner = get_or_create_user(
            db,
            email="owner@example.com",
            username="owner",
            password="OwnerPass1!",
        )
        admin = get_or_create_user(
            db,
            email="admin@example.com",
            username="admin",
            password="AdminPass1!",
        )
        member = get_or_create_user(
            db,
            email="member@example.com",
            username="member",
            password="MemberPass1!",
        )
        viewer = get_or_create_user(
            db,
            email="viewer@example.com",
            username="viewer",
            password="ViewerPass1!",
        )

        project = get_or_create_project(
            db,
            name="Issue Tracker Demo",
            key="DEMO",
            description="Demo project with seeded users, issues and labels",
            owner_id=owner.id,
        )

        get_or_create_membership(db, project_id=project.id, user_id=owner.id, role="owner")
        get_or_create_membership(db, project_id=project.id, user_id=admin.id, role="admin")
        get_or_create_membership(db, project_id=project.id, user_id=member.id, role="member")
        get_or_create_membership(db, project_id=project.id, user_id=viewer.id, role="viewer")

        bug_label = get_or_create_label(db, project_id=project.id, name="bug", color="#FF0000")
        backend_label = get_or_create_label(db, project_id=project.id, name="backend", color="#1D4ED8")
        auth_label = get_or_create_label(db, project_id=project.id, name="auth", color="#7C3AED")

        issue1 = get_or_create_issue(
            db,
            project_id=project.id,
            title="Implement JWT login",
            description="Add authentication and protected routes",
            status="in_progress",
            priority="high",
            reporter_id=owner.id,
            assignee_id=member.id,
        )

        issue2 = get_or_create_issue(
            db,
            project_id=project.id,
            title="Fix label validation",
            description="Ensure hex color validation works correctly",
            status="todo",
            priority="medium",
            reporter_id=admin.id,
            assignee_id=member.id,
        )

        issue3 = get_or_create_issue(
            db,
            project_id=project.id,
            title="Add pagination metadata",
            description="Return total, limit and offset in issue listing endpoint",
            status="done",
            priority="low",
            reporter_id=owner.id,
            assignee_id=admin.id,
        )

        attach_label_if_missing(db, issue_id=issue1.id, label_id=backend_label.id)
        attach_label_if_missing(db, issue_id=issue1.id, label_id=auth_label.id)
        attach_label_if_missing(db, issue_id=issue2.id, label_id=bug_label.id)
        attach_label_if_missing(db, issue_id=issue3.id, label_id=backend_label.id)

        print("Demo data seeded successfully.")
        print("Users:")
        print("  owner / OwnerPass1!")
        print("  admin / AdminPass1!")
        print("  member / MemberPass1!")
        print("  viewer / ViewerPass1!")
        print("Project key: DEMO")

    finally:
        db.close()


if __name__ == "__main__":
    main()