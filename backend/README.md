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
