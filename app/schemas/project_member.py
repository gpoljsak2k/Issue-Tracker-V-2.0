from typing import Literal
from pydantic import BaseModel, ConfigDict


class ProjectMemberCreate(BaseModel):
    username: str
    role: Literal["admin", "member", "viewer"]


class ProjectMemberUpdate(BaseModel):
    role: Literal["admin", "member", "viewer"]


class ProjectMemberUserResponse(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class ProjectMemberResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    role: str
    user: ProjectMemberUserResponse

    model_config = ConfigDict(from_attributes=True)