from typing import Literal
from pydantic import BaseModel, ConfigDict

class ProjectMemberCreate(BaseModel):
    user_id: int
    role: Literal["admin", "member", "viewer"]

class ProjectMemberResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    role:str

    model_config = ConfigDict(from_attributes=True)