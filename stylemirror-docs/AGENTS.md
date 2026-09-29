# AGENTS.md — Instructions for AI Coding Assistants

Applies to Antigravity, Claude Code, Cursor, Copilot, etc.

## Project
StyleMirror: hair & beard AI try-on website. Read `README.md`, then docs `01`–`10` before coding.

## Rules
1. Follow the specs in this folder; ask before deviating.
2. Work phase by phase (see `10_ROADMAP.md`). Finish and test each step before the next.
3. Backend: FastAPI, type hints everywhere, Pydantic schemas, async I/O, no business logic in routers (use `services/`).
4. AI calls only through the `ImageProvider` interface (`04_AI_PIPELINE.md`) using server-side API keys. Never call a vendor SDK from routers.
5. Frontend: **plain HTML, CSS and JavaScript (ES modules)** only. No React/Next.js, no bundler, no npm build step. Backend serves `frontend/` as static files.
5b. **No Docker.** Run everything with a Python venv + `uvicorn`.
5c. **API keys** for the AI provider live only in `backend/.env` (`GEMINI_API_KEYS=...`). Never put a key in frontend code, logs, commits or responses. Use the `KeyPool` pattern from `04_AI_PIPELINE.md`.
6. Never log image bytes or face embeddings. Never expose API keys to the client.
7. Every endpoint needs a pytest test and a documented error code.
8. Keep secrets in `.env`; provide `.env.example`.
9. Small commits with clear messages; one feature per PR/branch.
10. If the spec is ambiguous, state your assumption in the PR description.
11. **Auto-push to GitHub:** whenever you create a new folder and its files in **any language** (Dart, Python, TypeScript/JS, SQL, Kotlin, Swift, shell, config, docs, etc.), commit and push automatically — `git add -A && git commit -m "<type>(<scope>): <summary>" && git push origin HEAD`. Follow `11_GIT_WORKFLOW.md` (never commit secrets, no force push, run analyze/lint/tests first, stop and report if push fails).

## Definition of Done per Task
Code compiles/lints, tests pass, docs updated if behavior changed, no TODOs left without an issue.

## First Prompt
> Read all docs in this folder. Set up the project (`backend/` FastAPI in a Python venv, `frontend/` plain HTML/CSS/JS, no Docker). Implement `GET /styles`, `POST /photos`, `POST /generations`, `GET /generations/{id}` with the `ImageProvider` abstraction, a `GeminiProvider` and a `KeyPool` that reads `GEMINI_API_KEYS` from `.env`. Seed `styles` from `03_STYLE_CATALOG.md`. Then build `frontend/try.html` and the JS modules per `07_FRONTEND.md`. Auto-commit and push after each new folder/files. Work step by step and ask before deviating from the spec.

## Suggested Follow-up Prompts
1. "Write `scripts/crop_sheet.py` for my two style sheets and generate thumbnails."
2. "Implement face validation with MediaPipe per `04_AI_PIPELINE.md` thresholds."
3. "Add slowapi rate limiting, the daily cap and the 24 h cleanup task."
4. "Build the before/after slider and download button."
5. "Write a Playwright E2E test for upload → generate → delete against the local uvicorn server."
