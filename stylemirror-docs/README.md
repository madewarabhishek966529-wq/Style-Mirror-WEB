# StyleMirror — Hair & Beard AI Try-On Website

Upload a face photo → pick hairstyles / beard styles → see yourself with that look.

## Doc Index (read in this order)
| # | File | Purpose |
|---|---|---|
| 1 | `01_PRODUCT.md` | Vision, scope, user flow, phases |
| 2 | `02_ARCHITECTURE.md` | Stack, system design, project structure, env vars |
| 3 | `03_STYLE_CATALOG.md` | All 25 hairstyles + 25 beards, prompt hints, asset prep |
| 4 | `04_AI_PIPELINE.md` | Provider interface, prompts, identity check, cost control |
| 5 | `05_API_SPEC.md` | FastAPI endpoints, request/response, error codes |
| 6 | `06_DATABASE.md` | Postgres schema, cleanup jobs |
| 7 | `07_FRONTEND.md` | Pages, components, UX rules, design direction |
| 8 | `08_SECURITY_PRIVACY.md` | Consent, retention, DPDP/GDPR, abuse prevention |
| 9 | `09_TESTING_QA.md` | Acceptance criteria, test plan, edge cases |
| 10 | `10_ROADMAP.md` | Weekly plan, risks, definition of done |
| 11 | `11_GIT_WORKFLOW.md` | Auto commit + push to GitHub rules (all languages), `.gitignore`, safety checks |
| 12 | `AGENTS.md` | Rules + first prompt for AI coding assistants (Antigravity, Claude Code, Cursor) |

## Quick Summary
- **Frontend:** plain HTML + CSS + JavaScript (no framework, no build step)
- **Backend:** Python + FastAPI + Uvicorn (serves the frontend too)
- **AI:** hair/beard changed via hosted AI API using your **API keys** (Gemini primary, optional fallback) — keys stay in `backend/.env`
- **DB/Storage:** SQLite + local `storage/` folder (auto-deleted after 24 h)
- **No Docker** — run with a Python venv
- **Hosting:** Render / Railway / VPS running `uvicorn`

## Golden Rule
Edit the **user's own photo** with a text style description (+ optional reference). Never paste the user's face onto a demo model's photo — identity must be preserved.
