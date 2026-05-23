import os
from dataclasses import dataclass

import httpx
from fastapi import UploadFile
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class TranscriptionResult:
    raw_text: str
    optimized_text: str
    provider: str


class ASRServiceError(Exception):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


MOCK_RAW_TEXT = "今天下午三点我们开会讨论语音输入法开发计划"
MOCK_OPTIMIZED_TEXT = "今天下午三点，我们开会讨论语音输入法开发计划。"


def optimize_text(raw_text: str, mode: str) -> str:
    text = raw_text.strip()
    if not text:
        return ""

    if mode == "study":
        return text.replace("准确率速度成本还有易用性", "准确率、速度、成本和易用性。")

    if mode == "office" and not text.endswith(("。", "！", "？")):
        return f"{text}。"

    if text == MOCK_RAW_TEXT:
        return MOCK_OPTIMIZED_TEXT

    return text if text.endswith(("。", "！", "？")) else f"{text}。"


async def transcribe_audio(file: UploadFile, mode: str) -> TranscriptionResult:
    provider = os.getenv("ASR_PROVIDER", "mock").lower()

    if provider == "openai":
        raw_text = await transcribe_with_openai(file)
        return TranscriptionResult(
            raw_text=raw_text,
            optimized_text=optimize_text(raw_text, mode),
            provider="openai",
        )

    return TranscriptionResult(
        raw_text=MOCK_RAW_TEXT,
        optimized_text=MOCK_OPTIMIZED_TEXT,
        provider="mock",
    )


async def transcribe_with_openai(file: UploadFile) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ASRServiceError("OPENAI_API_KEY is required when ASR_PROVIDER=openai.")

    model = os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe")
    content = await file.read()
    if not content:
        raise ASRServiceError("Uploaded audio file is empty.")

    filename = file.filename or "recording.webm"
    content_type = file.content_type or "audio/webm"

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {api_key}"},
                data={
                    "model": model,
                    "response_format": "json",
                    "language": "zh",
                },
                files={"file": (filename, content, content_type)},
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as error:
        raise ASRServiceError(
            f"ASR provider returned {error.response.status_code}: {error.response.text}",
            status_code=error.response.status_code,
        ) from error
    except httpx.HTTPError as error:
        raise ASRServiceError(f"ASR provider request failed: {error}") from error

    data = response.json()
    text = data.get("text")
    if not isinstance(text, str):
        raise ASRServiceError("ASR provider response did not include text.")

    return text
