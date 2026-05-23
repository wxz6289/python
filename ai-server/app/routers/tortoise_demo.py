"""Tortoise ORM + MySQL 使用示例路由。"""

from fastapi import APIRouter, HTTPException, status
from tortoise.exceptions import DoesNotExist

from app.db.tortoise_models import Note
from app.schemas.response import set_response_msg
from app.schemas.tortoise_note import NoteCreate, NoteRead

router = APIRouter(prefix="/tortoise", tags=["tortoise"])


@router.post("/notes", status_code=status.HTTP_200_OK)
async def create_note(body: NoteCreate) -> NoteRead:
    note = await Note.create(title=body.title, content=body.content)
    set_response_msg("created")
    return NoteRead.model_validate(note)


@router.get("/notes")
async def list_notes() -> list[NoteRead]:
    notes = await Note.all().order_by("-id")
    return [NoteRead.model_validate(note) for note in notes]


@router.get("/notes/{note_id}")
async def get_note(note_id: int) -> NoteRead:
    try:
        note = await Note.get(id=note_id)
    except DoesNotExist as exc:
        raise HTTPException(status_code=404, detail="note not found") from exc
    return NoteRead.model_validate(note)


@router.delete("/notes/{note_id}")
async def delete_note(note_id: int) -> None:
    deleted = await Note.filter(id=note_id).delete()
    if not deleted:
        raise HTTPException(status_code=404, detail="note not found")
    set_response_msg("deleted")
