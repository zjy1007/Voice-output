from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.history_service import list_history, save_history

router = APIRouter(prefix="/api/history", tags=["history"])
TextMode = Literal["normal", "office", "study"]


class HistoryCreateRequest(BaseModel):
    text: str = Field(..., min_length=1)
    mode: TextMode = "normal"


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
