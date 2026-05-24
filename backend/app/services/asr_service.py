import asyncio
import base64
import hashlib
import hmac
import json
import os
import shutil
import ssl
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

import httpx
from dotenv import load_dotenv
from fastapi import UploadFile
import websocket

from app.services.text_service import (
    TextMode,
    TextOptimizationError,
    optimize_text_with_provider,
)

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


MOCK_RAW_TEXT = "今天下午三点我们开会讨论语音输入法开发计划然后整理需求"


async def transcribe_audio(file: UploadFile, mode: TextMode) -> TranscriptionResult:
    provider = os.getenv("ASR_PROVIDER", "mock").lower()

    if provider == "openai":
        raw_text = await transcribe_with_openai(file)
        optimized_text = await optimize_transcription(raw_text, mode)
        return TranscriptionResult(
            raw_text=raw_text,
            optimized_text=optimized_text,
            provider="openai",
        )

    if provider == "xfyun":
        raw_text = await asyncio.to_thread(transcribe_with_xfyun, file)
        optimized_text = await optimize_transcription(raw_text, mode)
        return TranscriptionResult(
            raw_text=raw_text,
            optimized_text=optimized_text,
            provider="xfyun",
        )

    optimized_text = await optimize_transcription(MOCK_RAW_TEXT, mode)
    return TranscriptionResult(
        raw_text=MOCK_RAW_TEXT,
        optimized_text=optimized_text,
        provider="mock",
    )


async def optimize_transcription(raw_text: str, mode: TextMode) -> str:
    try:
        return (await optimize_text_with_provider(raw_text, mode)).optimized_text
    except TextOptimizationError as error:
        raise ASRServiceError(str(error), status_code=error.status_code) from error


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


def transcribe_with_xfyun(file: UploadFile) -> str:
    app_id = os.getenv("XFYUN_APPID")
    api_key = os.getenv("XFYUN_API_KEY")
    api_secret = os.getenv("XFYUN_API_SECRET")

    if not app_id or not api_key or not api_secret:
        raise ASRServiceError(
            "XFYUN_APPID, XFYUN_API_KEY and XFYUN_API_SECRET are required when ASR_PROVIDER=xfyun.",
            status_code=400,
        )

    if not shutil.which("ffmpeg"):
        raise ASRServiceError(
            "ffmpeg is required to convert browser audio to 16kHz 16bit mono PCM.",
            status_code=500,
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = save_upload_to_temp_file(file, Path(temp_dir))
        pcm_path = Path(temp_dir) / "recording.pcm"
        convert_audio_to_pcm(input_path, pcm_path)
        return run_xfyun_iat(
            app_id=app_id,
            api_key=api_key,
            api_secret=api_secret,
            pcm_path=pcm_path,
        )


def save_upload_to_temp_file(file: UploadFile, temp_dir: Path) -> Path:
    suffix = Path(file.filename or "recording.webm").suffix or ".webm"
    input_path = temp_dir / f"upload{suffix}"
    file.file.seek(0)
    with input_path.open("wb") as output:
        shutil.copyfileobj(file.file, output)
    return input_path


def convert_audio_to_pcm(input_path: Path, pcm_path: Path) -> None:
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-f",
        "s16le",
        str(pcm_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise ASRServiceError(f"ffmpeg audio conversion failed: {result.stderr}", status_code=400)
    if not pcm_path.exists() or pcm_path.stat().st_size == 0:
        raise ASRServiceError("ffmpeg produced an empty PCM file.", status_code=400)


def create_xfyun_iat_url(api_key: str, api_secret: str) -> str:
    host = "ws-api.xfyun.cn"
    request_path = "/v2/iat"
    date = format_date_time(mktime(datetime.now().timetuple()))
    signature_origin = f"host: {host}\n"
    signature_origin += f"date: {date}\n"
    signature_origin += f"GET {request_path} HTTP/1.1"
    signature_sha = hmac.new(
        api_secret.encode("utf-8"),
        signature_origin.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    signature = base64.b64encode(signature_sha).decode("utf-8")
    authorization_origin = (
        f'api_key="{api_key}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode("utf-8")
    return "wss://ws-api.xfyun.cn/v2/iat?" + urlencode(
        {
            "authorization": authorization,
            "date": date,
            "host": host,
        }
    )


def run_xfyun_iat(
    app_id: str,
    api_key: str,
    api_secret: str,
    pcm_path: Path,
) -> str:
    done = threading.Event()
    error_messages: list[str] = []
    result_parts: list[str] = []
    send_errors: list[str] = []
    send_stats = {
        "pcm_bytes": pcm_path.stat().st_size,
        "frames": 0,
        "first_frame_sent": False,
        "last_frame_sent": False,
    }

    def on_message(ws: websocket.WebSocketApp, message: str) -> None:
        try:
            payload = json.loads(message)
            code = payload.get("code")
            if code != 0:
                error_messages.append(
                    f"XFYun returned {code}: {payload.get('message', 'unknown error')}"
                )
                done.set()
                ws.close()
                return

            for segment in payload.get("data", {}).get("result", {}).get("ws", []):
                for candidate in segment.get("cw", []):
                    result_parts.append(candidate.get("w", ""))
        except Exception as error:
            error_messages.append(f"Failed to parse XFYun response: {error}")
            done.set()
            ws.close()

    def on_error(_ws: websocket.WebSocketApp, error: object) -> None:
        error_messages.append(f"XFYun websocket error: {error}; send_stats={send_stats}")
        done.set()

    def on_close(
        _ws: websocket.WebSocketApp,
        _close_status_code: object,
        _close_msg: object,
    ) -> None:
        done.set()

    def on_open(ws: websocket.WebSocketApp) -> None:
        thread = threading.Thread(
            target=send_xfyun_audio_frames,
            args=(ws, app_id, pcm_path, send_errors, done, send_stats),
        )
        thread.daemon = True
        thread.start()

    ws_url = create_xfyun_iat_url(api_key, api_secret)
    ws = websocket.WebSocketApp(
        ws_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
    )
    runner = threading.Thread(
        target=lambda: ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    )
    runner.daemon = True
    runner.start()

    if not done.wait(timeout=90):
        ws.close()
        raise ASRServiceError("XFYun transcription timed out.")

    runner.join(timeout=2)

    if error_messages:
        raise ASRServiceError(error_messages[0])
    if send_errors:
        raise ASRServiceError(send_errors[0])

    raw_text = "".join(result_parts).strip()
    if not raw_text:
        raise ASRServiceError("XFYun transcription returned empty text.")

    return raw_text


def send_xfyun_audio_frames(
    ws: websocket.WebSocketApp,
    app_id: str,
    pcm_path: Path,
    send_errors: list[str],
    done: threading.Event,
    send_stats: dict[str, object],
) -> None:
    frame_size = 8000
    interval = 0.04
    status_first_frame = 0
    status_continue_frame = 1
    status_last_frame = 2
    status = status_first_frame

    try:
        with pcm_path.open("rb") as file:
            while True:
                buffer = file.read(frame_size)
                if not buffer:
                    status = status_last_frame

                if status == status_first_frame:
                    payload = {
                        "common": {"app_id": app_id},
                        "business": {
                            "domain": "iat",
                            "language": "zh_cn",
                            "accent": "mandarin",
                            "vinfo": 1,
                            "vad_eos": 10000,
                        },
                        "data": {
                            "status": 0,
                            "format": "audio/L16;rate=16000",
                            "audio": base64.b64encode(buffer).decode("utf-8"),
                            "encoding": "raw",
                        },
                    }
                    ws.send(json.dumps(payload))
                    send_stats["frames"] = int(send_stats["frames"]) + 1
                    send_stats["first_frame_sent"] = True
                    status = status_continue_frame
                elif status == status_continue_frame:
                    payload = {
                        "data": {
                            "status": 1,
                            "format": "audio/L16;rate=16000",
                            "audio": base64.b64encode(buffer).decode("utf-8"),
                            "encoding": "raw",
                        }
                    }
                    ws.send(json.dumps(payload))
                    send_stats["frames"] = int(send_stats["frames"]) + 1
                elif status == status_last_frame:
                    payload = {
                        "data": {
                            "status": 2,
                            "format": "audio/L16;rate=16000",
                            "audio": base64.b64encode(buffer).decode("utf-8"),
                            "encoding": "raw",
                        }
                    }
                    ws.send(json.dumps(payload))
                    send_stats["frames"] = int(send_stats["frames"]) + 1
                    send_stats["last_frame_sent"] = True
                    time.sleep(1)
                    ws.close()
                    break

                time.sleep(interval)
    except Exception as error:
        send_errors.append(f"Failed to send audio frames to XFYun: {error}")
        done.set()
        ws.close()
