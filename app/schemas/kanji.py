from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class KanjiListItem(BaseModel):
    id: UUID
    character: str
    meanings: list[str]
    stroke_count: int
    jlpt_level: int | None
    radicals: list[str] | None
    frequency: int | None
    school_level: int | None
    bg_meanings: list[str] | None = None

    model_config = ConfigDict(from_attributes=True)


class KanjiByCharacterResponse(BaseModel):
    id: UUID
    character: str
    meanings: list[str]
    stroke_count: int
    jlpt_level: int | None
    radicals: list[str] | None
    frequency: int | None
    school_level: int | None
    bg_meanings: list[str] | None = None
    stroke_data: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)


class KanjiListResponse(BaseModel):
    items: list[KanjiListItem]
    next_cursor: str | None
