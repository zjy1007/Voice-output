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
