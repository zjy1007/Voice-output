from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.history_service import delete_history, list_history, save_history, update_history

router = APIRouter(prefix="/api/history", tags=["history"])
TextMode = Literal["normal", "office", "study", "prompt"]


class HistoryCreateRequest(BaseModel):
    text: str = Field(..., min_length=1)
    mode: TextMode = "normal"


class HistoryUpdateRequest(BaseModel):
    text: str = Field(..., min_length=1)
    mode: TextMode | None = None


@router.get("")
def get_history() -> dict[str, object]:
    return {
        "code": 200,
        "message": "success",
        "data": list_history(),
    }


@router.post("")
def create_history(request: HistoryCreateRequest) -> dict[str, object]:
    try:
        record = save_history(request.text, request.mode)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "code": 200,
        "message": "history saved",
        "data": record,
    }


@router.patch("/{record_id}")
def patch_history(record_id: int, request: HistoryUpdateRequest) -> dict[str, object]:
    try:
        record = update_history(record_id, request.text, request.mode)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "code": 200,
        "message": "history updated",
        "data": record,
    }


@router.delete("/{record_id}")
def remove_history(record_id: int) -> dict[str, object]:
    try:
        delete_history(record_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return {
        "code": 200,
        "message": "history deleted",
        "data": {"id": record_id},
    }
