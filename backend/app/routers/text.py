from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.text_service import TextOptimizationError, optimize_text_with_provider

router = APIRouter(prefix="/api/text", tags=["text"])

TextMode = Literal["normal", "office", "study"]


class TextOptimizeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    mode: TextMode = "normal"


@router.post("/optimize")
async def optimize_text_endpoint(request: TextOptimizeRequest) -> dict[str, object]:
    try:
        result = await optimize_text_with_provider(request.text, request.mode)
    except TextOptimizationError as error:
        raise HTTPException(status_code=error.status_code, detail=str(error)) from error

    return {
        "code": 200,
        "message": "success",
        "data": {
            "original_text": result.original_text,
            "optimized_text": result.optimized_text,
            "mode": result.mode,
            "provider": result.provider,
        },
    }
