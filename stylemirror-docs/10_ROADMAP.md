# 10 — Roadmap, Risks & Definition of Done

## Weekly Plan
| Week | Deliverable |
|---|---|
| 1 | Repo setup, Python venv + FastAPI skeleton, `.env.example`, crop reference sheets, seed `styles`, `GET /styles`, static HTML shell |
| 2 | `POST /photos`, local storage, face validation, uploader + tips UI (HTML/CSS/JS) |
| 3 | Gemini provider with API key pool, prompts, generation job + polling, result section |
| 4 | Style grid UI, hair+beard combo, before/after slider, download |
| 5 | Caching, `slowapi` rate limits, daily cap, cleanup task, consent + delete, Sentry/PostHog |
| 6 | Landing page, golden-set QA, bug fixes, deploy (Render/Railway running `uvicorn`, no Docker) |
| 7+ | Phase 2: auth, saved looks, suggestions, hair color, multi-view |

## Risks & Mitigations
| Risk | Mitigation |
|---|---|
| Face changes / looks like someone else | Strong identity prompt, identity score + retry, prefer text hints over reference faces |
| Beard looks pasted / wrong color | Prompt: match hair color, grow along jawline; regenerate button |
| Side/back views inconsistent | Mark beta, Phase 2 only |
| API cost spikes | Lazy generation, caching, rate limits, per-user cap, cost logging |
| Slow generation | Queue + progress UI, downscale input |
| Abuse / deepfakes | Consent, own-photo checkbox, watermark, rate limits, provider safety filters |
| Provider outage / policy change | `ImageProvider` abstraction + fallback |

## Definition of Done (MVP)
- [ ] Upload + validation with clear error messages
- [ ] All 25 hairstyles and 25 beards selectable with thumbnails
- [ ] Hair-only, beard-only, combo generation end-to-end
- [ ] Before/after slider + download
- [ ] 24 h auto-delete and manual delete work
- [ ] Rate limiting + caching active
- [ ] Privacy policy, terms, consent checkbox live
- [ ] Deployed with monitoring and documented README
