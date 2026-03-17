from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CommentAuthorResponse(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    body: str


class CommentUpdate(BaseModel):
    body: str


class CommentResponse(BaseModel):
    id: int
    issue_id: int
    author_id: int
    body: str
    created_at: datetime
    author: CommentAuthorResponse

    model_config = ConfigDict(from_attributes=True)