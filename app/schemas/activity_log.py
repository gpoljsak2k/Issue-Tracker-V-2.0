from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ActivityActorResponse(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class ActivityLogResponse(BaseModel):
    id: int
    project_id: int
    issue_id: int | None
    actor_id: int
    actor: ActivityActorResponse
    action: str
    metadata_json: dict[str, Any] | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)