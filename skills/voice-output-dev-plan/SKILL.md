---
name: voice-output-dev-plan
description: Use this skill when planning, implementing, or reviewing development work for the Voice-output intelligent voice input method MVP described in the project README. It guides phase planning, task slicing, architecture choices, acceptance criteria, and test strategy for the React/Vue + TypeScript frontend, FastAPI backend, ASR integration, text optimization, hotword management, and history features.
---

# Voice-output Development Plan

## Purpose

Use this skill to turn the Voice-output README into concrete development work. The project goal is a web MVP for intelligent voice input:

```text
record audio -> upload -> ASR -> punctuation/text optimization -> mode-specific formatting -> edit/copy/save
```

Favor a runnable MVP before advanced extensions. Keep every task tied to one user-visible flow, API contract, or persistence behavior.

## Core Product Scope

Build these MVP capabilities first:

- Web recording flow: microphone permission, start/stop recording, upload audio, show progress/errors.
- ASR endpoint: `POST /api/asr/transcribe` accepts `file` and `mode`, returns `raw_text` and `optimized_text`.
- Text optimization endpoint: `POST /api/text/optimize` handles punctuation, sentence splitting, and modes `normal`, `office`, `study`.
- Hotwords: `GET /api/hotwords`, `POST /api/hotwords`; use hotwords for correction where feasible.
- History: `GET /api/history`, `POST /api/history`; save optimized text, mode, and timestamp.
- Editor workflow: display result, allow editing, copy, clear, append input, delete previous segment, save history.

Treat real-time streaming recognition, offline models, mobile input method, user accounts, multilingual support, and analytics dashboards as post-MVP unless the user explicitly reprioritizes them.

## Development Workflow

1. **Confirm current repo state**
   - Inspect existing files before editing.
   - Check `README.md`, current directory structure, package files, backend files, and tests if present.
   - Do not assume the README structure has already been created.

2. **Slice work by vertical features**
   - Prefer end-to-end slices over isolated layers.
   - Good first slice: backend health route + frontend shell + API wiring.
   - Good second slice: text optimization endpoint + UI mode selector + transcript editor.
   - Good third slice: recording/upload flow + mock or pluggable ASR service.

3. **Keep architecture simple**
   - Frontend: `src/api`, `src/components`, `src/hooks`, `src/pages`, `src/utils`.
   - Backend: `app/main.py`, `routers`, `services`, `schemas`, `utils`, `database.py`.
   - Keep ASR behind a service interface so mock, third-party API, Faster-Whisper, or FunASR can be swapped.
   - Use SQLite for MVP persistence unless the user requests another database.

4. **Define acceptance criteria before coding**
   - Each task should include API behavior, UI behavior, error behavior, and tests or manual verification.
   - Include sample Chinese input from the README when testing text optimization.

5. **Implement with graceful fallbacks**
   - If ASR credentials or local ASR models are unavailable, provide a mock/demo ASR path for the UI and API flow.
   - Keep environment variables documented where they are introduced.
   - Return consistent JSON: `code`, `message`, `data`.

6. **Verify the user flow**
   - Backend: run unit/API tests where available.
   - Frontend: run typecheck/build where available.
   - Manual flow: open app, record or upload demo audio, view optimized text, switch modes, add hotword, copy/clear/save, view history.

## Planning Output Format

When asked to plan, produce:

- Current assumption: what exists locally and what still needs to be created.
- Milestones: 3 to 6 phases, ordered by user-visible value.
- Task list: small implementation tasks with clear outputs.
- Acceptance criteria: how to know each phase is done.
- Risks: ASR choice, browser microphone permissions, API key/model availability, Chinese punctuation quality.
- First next step: the smallest concrete action to start.

For a detailed MVP roadmap, read `references/mvp-roadmap.md`.

## Implementation Priorities

Default priority order:

1. Project scaffolding and local startup commands.
2. Backend API contracts and schemas.
3. Text optimization logic with deterministic mode examples.
4. Hotword and history persistence.
5. Frontend recording/editor workflow.
6. ASR provider integration.
7. Tests, demo script, and polish.

## Quality Bar

- The app must run locally with documented commands.
- API responses must match README examples unless a change is intentionally explained.
- The UI should be the usable app immediately, not a marketing landing page.
- Text should fit on mobile and desktop.
- Errors should be visible and recoverable, especially microphone denial and upload failure.
- Tests should cover text optimization, hotword CRUD, history save/list, and ASR endpoint error paths.
