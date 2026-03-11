import re

from pydantic import BaseModel, Field, ConfigDict, field_validator


class LabelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    color: str = Field(min_length=4, max_length=20)

    @field_validator("color")
    @classmethod
    def validate_color(cls, value: str) -> str:
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
            raise ValueError("Color must be a valid hex code like #FF5733")
        return value


class LabelResponse(BaseModel):
    id: int
    project_id: int
    name: str
    color: str

    model_config = ConfigDict(from_attributes=True)


class IssueLabelAttach(BaseModel):
    label_id: int