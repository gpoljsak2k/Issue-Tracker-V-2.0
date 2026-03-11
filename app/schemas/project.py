import re

from pydantic import BaseModel, Field, ConfigDict, field_validator


class ProjectCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    key: str = Field(min_length=2, max_length=10)
    description: str | None = Field(default=None, max_length=1000)

    @field_validator("key")
    @classmethod
    def validate_key(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Z0-9]+", value):
            raise ValueError("Project key must contain only uppercase letters and numbers")
        return value


class ProjectResponse(BaseModel):
    id: int
    name: str
    key: str
    description: str | None
    owner_id: int

    model_config = ConfigDict(from_attributes=True)