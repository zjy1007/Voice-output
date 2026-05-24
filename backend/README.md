# Voice-output Backend

FastAPI backend for the Voice-output MVP.

## Start

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs:

```text
http://localhost:8000/docs
```

## ASR Provider

The backend uses a mock ASR response by default, so the frontend flow can run without credentials.

To call the real OpenAI-compatible transcription API:

```bash
cp .env.example .env
# Edit .env and set:
# ASR_PROVIDER=openai
# OPENAI_API_KEY=your_api_key
# OPENAI_TRANSCRIBE_MODEL=gpt-4o-mini-transcribe
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Text Optimizer Provider

Text optimization uses local rules by default.

To use DeepSeek V4 for punctuation, sentence splitting, and mode-based rewriting:

```bash
cp .env.example .env
# Edit .env and set:
# TEXT_OPTIMIZER_PROVIDER=deepseek
# DEEPSEEK_API_KEY=your_deepseek_api_key
# DEEPSEEK_BASE_URL=https://api.deepseek.com
# DEEPSEEK_MODEL=deepseek-v4-flash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Use `deepseek-v4-flash` for lower latency/cost, or `deepseek-v4-pro` for stronger rewriting quality.

## XFYun ASR Provider

To use iFlytek/XFYun streaming speech dictation:

```bash
cp .env.example .env
# Edit .env and set:
# ASR_PROVIDER=xfyun
# XFYUN_APPID=your_appid
# XFYUN_API_KEY=your_api_key
# XFYUN_API_SECRET=your_api_secret
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Browser recordings are usually `audio/webm`. The backend converts uploaded audio to 16kHz, 16bit, mono PCM before sending it to XFYun, so `ffmpeg` must be installed locally:

```bash
brew install ffmpeg
```
