from sqlalchemy import delete, select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.activity_log import ActivityLog
from app.models.comment import Comment
from app.models.issue import Issue
from app.models.issue_label import IssueLabel
from app.models.label import Label
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User


def reset_database(db):
    # Delete in dependency order
    db.execute(delete(Comment))
    db.execute(delete(IssueLabel))
    db.execute(delete(ActivityLog))
    db.execute(delete(Issue))
    db.execute(delete(Label))
    db.execute(delete(ProjectMember))
    db.execute(delete(Project))
    db.execute(delete(User))
    db.commit()


def seed_users(db):
    admin = User(
        email="admin@example.com",
        username="admin",
        hashed_password=hash_password("Admin123!"),
        is_active=True,
    )
    ana = User(
        email="ana@example.com",
        username="ana",
        hashed_password=hash_password("Ana12345!"),
        is_active=True,
    )
    matej = User(
        email="matej@example.com",
        username="matej",
        hashed_password=hash_password("Matej123!"),
        is_active=True,
    )

    db.add_all([admin, ana, matej])
    db.commit()

    for user in [admin, ana, matej]:
        db.refresh(user)

    return admin, ana, matej


def seed_project(db, owner):
    project = Project(
        name="Issue Tracker Demo",
        key="DEMO",
        description="Demo project for presentation",
        owner_id=owner.id,
    )
    db.add(project)
    db.flush()

    owner_membership = ProjectMember(
        project_id=project.id,
        user_id=owner.id,
        role="owner",
    )
    db.add(owner_membership)

    db.commit()
    db.refresh(project)
    return project


def seed_members(db, project, ana, matej):
    members = [
        ProjectMember(project_id=project.id, user_id=ana.id, role="admin"),
        ProjectMember(project_id=project.id, user_id=matej.id, role="member"),
    ]
    db.add_all(members)
    db.commit()


def seed_labels(db, project):
    labels = [
        Label(project_id=project.id, name="backend", color="#dbeafe"),
        Label(project_id=project.id, name="frontend", color="#fef3c7"),
        Label(project_id=project.id, name="bug", color="#fee2e2"),
        Label(project_id=project.id, name="urgent", color="#fecaca"),
    ]
    db.add_all(labels)
    db.commit()

    for label in labels:
        db.refresh(label)

    return labels


def seed_issues(db, project, admin, ana, matej):
    issues = [
        Issue(
            project_id=project.id,
            title="Add pagination metadata",
            description="Expose total, limit and offset in the issues response.",
            status="todo",
            priority="high",
            reporter_id=admin.id,
            assignee_id=matej.id,
        ),
        Issue(
            project_id=project.id,
            title="Improve login page styling",
            description="Add app title and improve spacing on the login form.",
            status="in_progress",
            priority="medium",
            reporter_id=admin.id,
            assignee_id=ana.id,
        ),
        Issue(
            project_id=project.id,
            title="Fix issue labels UI",
            description="Make sure labels can be added and removed from the issue details panel.",
            status="in_review",
            priority="high",
            reporter_id=ana.id,
            assignee_id=admin.id,
        ),
        Issue(
            project_id=project.id,
            title="Prepare demo data",
            description="Seed realistic demo users, project, issues and comments.",
            status="done",
            priority="urgent",
            reporter_id=admin.id,
            assignee_id=admin.id,
        ),
        Issue(
            project_id=project.id,
            title="Add project activity panel",
            description="Show recent project activity below the issues list.",
            status="blocked",
            priority="medium",
            reporter_id=matej.id,
            assignee_id=None,
        ),
    ]

    db.add_all(issues)
    db.commit()

    for issue in issues:
        db.refresh(issue)

    return issues


def seed_issue_labels(db, issues, labels):
    label_by_name = {label.name: label for label in labels}

    mappings = [
        (issues[0], ["backend"]),
        (issues[1], ["frontend"]),
        (issues[2], ["frontend", "bug"]),
        (issues[3], ["urgent"]),
        (issues[4], ["backend", "bug"]),
    ]

    rows = []
    for issue, names in mappings:
        for name in names:
            label = label_by_name.get(name)
            if label:
                rows.append(IssueLabel(issue_id=issue.id, label_id=label.id))

    db.add_all(rows)
    db.commit()

def seed_comments(db, issues, admin, ana, matej):
    comments = [
        Comment(
            issue_id=issues[0].id,
            author_id=admin.id,
            body="We should keep this response consistent with project activity pagination later.",
        ),
        Comment(
            issue_id=issues[0].id,
            author_id=matej.id,
            body="I can take this one after the labels work is finished.",
        ),
        Comment(
            issue_id=issues[1].id,
            author_id=ana.id,
            body="I already improved the login title, just polishing the spacing now.",
        ),
        Comment(
            issue_id=issues[3].id,
            author_id=admin.id,
            body="This issue is here mainly so the demo has at least one completed task.",
        ),
    ]

    db.add_all(comments)
    db.commit()


from app.models.user import User

def main():
    db = SessionLocal()
    try:
        existing_user = db.execute(select(User)).first()

        if existing_user:
            print("Data already exists, skipping seed.")
            return

        print("Creating demo users...")
        admin, ana, matej = seed_users(db)

        print("Creating demo project...")
        project = seed_project(db, admin)

        print("Creating project members...")
        seed_members(db, project, ana, matej)

        print("Creating labels...")
        labels = seed_labels(db, project)

        print("Creating issues...")
        issues = seed_issues(db, project, admin, ana, matej)

        print("Attaching labels to issues...")
        seed_issue_labels(db, issues, labels)

        print("Creating comments...")
        seed_comments(db, issues, admin, ana, matej)

        print("\nDemo seed complete.")

    finally:
        db.close()

if __name__ == "__main__":
    main()