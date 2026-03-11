from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class IssueLabel(Base):
    __tablename__ = "issue_labels"
    __table_args__ = (
        UniqueConstraint("issue_id", "label_id", name="uq_issue_label_issue_label"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"), nullable=False, index=True)
    label_id: Mapped[int] = mapped_column(ForeignKey("labels.id"), nullable=False, index=True)