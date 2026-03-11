from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class IssueCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    status: Literal["todo", "in_progress", "in_review", "done", "blocked"] = "todo"
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    assignee_id: int | None = None


class IssueResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    priority: str
    project_id: int
    reporter_id: int
    assignee_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class IssueUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    status: Literal["todo", "in_progress", "in_review", "done", "blocked"] | None = None
    priority: Literal["low", "medium", "high", "urgent"] | None = None
    assignee_id: int | None = None