import uuid

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Kanji(Base):
    __tablename__ = "kanji"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    character: Mapped[str] = mapped_column(String, nullable=False)
    meanings: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    stroke_count: Mapped[int] = mapped_column(Integer, nullable=False)
    jlpt_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stroke_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    radicals: Mapped[list[str | None] | None] = mapped_column(ARRAY(Text), nullable=True)
    frequency: Mapped[int | None] = mapped_column(Integer, nullable=True)
    inserted_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    translations: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    school_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
