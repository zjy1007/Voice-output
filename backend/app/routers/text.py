from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.text_service import optimize_text

router = APIRouter(prefix="/api/text", tags=["text"])

TextMode = Literal["normal", "office", "study"]


class TextOptimizeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    mode: TextMode = "normal"


@router.post("/optimize")
def optimize_text_endpoint(request: TextOptimizeRequest) -> dict[str, object]:
    result = optimize_text(request.text, request.mode)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "original_text": result.original_text,
            "optimized_text": result.optimized_text,
            "mode": result.mode,
        },
    }
