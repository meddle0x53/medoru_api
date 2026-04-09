from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Select, and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import decode_cursor, encode_cursor
from app.db.session import get_db
from app.models.kanji import Kanji
from app.schemas.kanji import (
    KanjiByCharacterResponse,
    KanjiListItem,
    KanjiListResponse,
)

router = APIRouter(prefix="/kanji", tags=["kanji"])

ALLOWED_INCLUDES = {"bg_meanings"}


def parse_include(include: str | None) -> set[str]:
    if not include:
        return set()

    values = {part.strip() for part in include.split(",") if part.strip()}
    unknown = values - ALLOWED_INCLUDES
    if unknown:
        unknown_str = ", ".join(sorted(unknown))
        raise HTTPException(status_code=400, detail=f"Unknown include value(s): {unknown_str}")

    return values


def extract_bg_meanings(translations: dict | None) -> list[str] | None:
    if not translations:
        return None

    bg = translations.get("bg")
    if not isinstance(bg, dict):
        return None

    meanings = bg.get("meanings")
    if not isinstance(meanings, list):
        return None

    return [str(item) for item in meanings]

def clean_str_list(values: list[str | None] | None) -> list[str] | None:
    if values is None:
        return None

    cleaned = [value for value in values if value is not None]
    return cleaned

@router.get("", response_model=KanjiListResponse)
async def list_kanji(
    jlpt_level: int | None = Query(default=None, ge=1, le=5),
    limit: int = Query(default=50, ge=1, le=100),
    cursor: str | None = Query(default=None),
    include: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> KanjiListResponse:
    include_fields = parse_include(include)

    stmt: Select = select(Kanji)

    filters = []
    if jlpt_level is not None:
        filters.append(Kanji.jlpt_level == jlpt_level)

    if filters:
        stmt = stmt.where(and_(*filters))

    if cursor:
        try:
            payload = decode_cursor(cursor)
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Invalid cursor") from exc

        cursor_jlpt_level = payload.get("jlpt_level")
        if cursor_jlpt_level != jlpt_level:
            raise HTTPException(
                status_code=400,
                detail="Cursor does not match current filters",
            )

        last_character = payload.get("character")
        last_id = payload.get("id")
        if not isinstance(last_character, str) or not isinstance(last_id, str):
            raise HTTPException(status_code=400, detail="Invalid cursor payload")

        stmt = stmt.where(
            or_(
                Kanji.character > last_character,
                and_(Kanji.character == last_character, Kanji.id > UUID(last_id)),
            )
        )

    stmt = stmt.order_by(Kanji.character.asc(), Kanji.id.asc()).limit(limit + 1)

    result = await db.execute(stmt)
    rows = result.scalars().all()

    has_next = len(rows) > limit
    items = rows[:limit]

    response_items = [
        KanjiListItem(
            id=item.id,
            character=item.character,
            meanings=clean_str_list(item.meanings) or [],
            stroke_count=item.stroke_count,
            jlpt_level=item.jlpt_level,
            radicals=clean_str_list(item.radicals),
            frequency=item.frequency,
            school_level=item.school_level,
            bg_meanings=extract_bg_meanings(item.translations)
            if "bg_meanings" in include_fields
            else None,
        )
        for item in items
    ]

    next_cursor = None
    if has_next and items:
        last_item = items[-1]
        next_cursor = encode_cursor(
            {
                "character": last_item.character,
                "id": str(last_item.id),
                "jlpt_level": jlpt_level,
            }
        )

    return KanjiListResponse(items=response_items, next_cursor=next_cursor)


@router.get("/character/{character}", response_model=KanjiByCharacterResponse)
async def get_kanji_by_character(
    character: str,
    include: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> KanjiByCharacterResponse:
    include_fields = parse_include(include)

    stmt = select(Kanji).where(Kanji.character == character).limit(1)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(status_code=404, detail="Kanji not found")

    return KanjiByCharacterResponse(
        id=item.id,
        character=item.character,
        meanings=clean_str_list(item.meanings) or [],
        stroke_count=item.stroke_count,
        jlpt_level=item.jlpt_level,
        radicals=clean_str_list(item.radicals),
        frequency=item.frequency,
        school_level=item.school_level,
        bg_meanings=extract_bg_meanings(item.translations)
        if "bg_meanings" in include_fields
        else None,
        stroke_data=item.stroke_data,
    )
