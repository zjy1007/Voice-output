from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.hotword_service import add_hotword, list_hotwords

router = APIRouter(prefix="/api/hotwords", tags=["hotwords"])


class HotwordCreateRequest(BaseModel):
    word: str = Field(..., min_length=1)


@router.get("")
def get_hotwords() -> dict[str, object]:
    return {
        "code": 200,
        "message": "success",
        "data": list_hotwords(),
    }


@router.post("")
def create_hotword(request: HotwordCreateRequest) -> dict[str, object]:
    try:
        word = add_hotword(request.word)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "code": 200,
        "message": "hotword added",
        "data": {"word": word},
    }
