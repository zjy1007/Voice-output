from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.asr_service import ASRServiceError, transcribe_audio as transcribe_audio_file

router = APIRouter(prefix="/api/asr", tags=["asr"])


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    mode: str = Form("normal"),
) -> dict[str, object]:
    try:
        result = await transcribe_audio_file(file, mode)
    except ASRServiceError as error:
        raise HTTPException(status_code=error.status_code, detail=str(error)) from error

    return {
        "code": 200,
        "message": "success",
        "data": {
            "filename": file.filename,
            "mode": mode,
            "provider": result.provider,
            "raw_text": result.raw_text,
            "optimized_text": result.optimized_text,
        },
    }
