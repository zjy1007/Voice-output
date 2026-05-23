# Voice-output MVP Roadmap

## Phase 0: Repository Baseline

Goal: create a clean, runnable project foundation.

Tasks:
- Create `frontend/`, `backend/`, and `docs/` directories if missing.
- Add `.gitignore` for Python, Node, build artifacts, virtualenvs, environment files, and OS files.
- Add backend `requirements.txt`.
- Add frontend package setup with Vite and TypeScript if the user wants React/Vue implementation.
- Add `docs/product_design.md`, `docs/technical_design.md`, and `docs/demo_script.md` as living documents.

Acceptance criteria:
- Repo has the README-aligned structure.
- Backend and frontend install commands are clear.
- Sensitive files such as `.env` are ignored.

## Phase 1: Backend Skeleton

Goal: expose stable FastAPI routes and response models.

Tasks:
- Create `backend/app/main.py`.
- Create routers: `asr.py`, `text.py`, `hotword.py`, `history.py`.
- Create Pydantic schemas for common response shape and request bodies.
- Add CORS for local frontend development.
- Add a health endpoint.

Acceptance criteria:
- `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` starts.
- `http://localhost:8000/docs` shows the API routes.
- Routes return consistent JSON: `code`, `message`, `data`.

## Phase 2: Text Optimization

Goal: make the app useful even before real ASR is integrated.

Tasks:
- Implement `POST /api/text/optimize`.
- Support modes:
  - `normal`: preserve natural expression with punctuation cleanup.
  - `office`: make phrasing more formal and complete.
  - `study`: convert enumerations into structured notes where possible.
- Add tests for README examples.

Acceptance criteria:
- The README sample for `study` mode returns a list-like optimized text.
- Empty or invalid text returns a clear error.
- Unknown mode falls back safely or returns a validation error.

## Phase 3: Persistence

Goal: support hotwords and history for a complete input loop.

Tasks:
- Add SQLite connection and initialization.
- Implement hotword list/add endpoints.
- Implement history save/list endpoints.
- Keep timestamps in a consistent format.

Acceptance criteria:
- Added hotwords persist after server restart.
- Saved history records include `id`, `text`, `mode`, and `created_at`.
- Tests cover add/list flows and duplicate or invalid input behavior.

## Phase 4: ASR Integration

Goal: connect audio upload to recognition while preserving a demo path.

Tasks:
- Implement `POST /api/asr/transcribe` with `file` and `mode`.
- Add `asr_service.py` with a provider boundary.
- Support a mock provider for local development.
- Add environment-driven provider selection for third-party API or local model.
- Run transcript through text optimization before returning.

Acceptance criteria:
- Uploading an audio file returns both `raw_text` and `optimized_text`.
- Missing/invalid file returns a clear error.
- The app remains demoable without paid API credentials or local model downloads.

## Phase 5: Frontend MVP

Goal: deliver the complete web input experience.

Tasks:
- Create the main app page, API clients, and recording hook.
- Components:
  - `RecorderButton`
  - `TranscriptEditor`
  - `ModeSelector`
  - `HotwordPanel`
  - `HistoryList`
  - `ResultToolbar`
- Use `MediaRecorder` for browser audio capture.
- Implement copy, clear, append, delete previous segment, save history.

Acceptance criteria:
- User can record, stop, submit, view optimized result, edit, copy, save, and see history.
- Microphone denial and upload failures are visible and recoverable.
- UI works on desktop and mobile widths.

## Phase 6: Demo And Polish

Goal: make the project easy to present and evaluate.

Tasks:
- Add focused backend tests.
- Run frontend build/typecheck.
- Update docs with startup and demo steps.
- Prepare demo script following README order.

Acceptance criteria:
- A fresh clone can run the backend and frontend from documented commands.
- Demo covers ordinary input, office mode, study notes, hotwords, copy/clear/save, history, and API docs.
- Known limitations and next improvements are documented.
