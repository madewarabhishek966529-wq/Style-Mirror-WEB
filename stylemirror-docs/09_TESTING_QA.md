# 09 — Testing & QA

## MVP Acceptance Criteria
- Valid selfie → result in < 20 s (p90).
- Identity similarity ≥ 0.6 on ≥ 90% of test photos.
- Non-target areas (clothes, background) visibly unchanged.
- Works on Chrome/Safari, mobile + desktop.
- Deleting a photo removes all outputs within 1 minute.

## Test Plan
| Level | What |
|---|---|
| Unit | Prompt builder, face-check thresholds, cache-key logic |
| API | pytest + httpx for every endpoint and error code |
| Golden set | 30 diverse selfies (skin tones, ages, lighting, glasses, existing beards) × 10 styles → manual review sheet |
| E2E | Playwright: upload → pick → result → delete |
| Load | 50 concurrent generations; background tasks hold, no timeouts |
| Keys | Invalid key, exhausted quota, key rotation, fallback provider |
| Security | Oversized/invalid files, expired file tokens, IDOR on photo/job IDs, confirm no API key appears in any served HTML/JS/response |

## Edge Cases
- Bald user + long hair style
- Existing full beard → Clean Shaven
- Long hair → Buzz Cut
- Glasses, caps, headwear (turban/hijab → reject politely)
- Low light, backlit, very high-res, rotated EXIF
- Two faces in frame, no face, cartoon/non-human image
- Provider timeout / safety block → friendly retry message

## Golden-Set Review Rubric (score 1–5)
Identity preserved · Style matches name · Natural blending · Background/clothes unchanged · No artifacts (hands, ears, hairline).
Track average per style; styles scoring < 3.5 get prompt tuning.

## Tools
pytest, httpx, Playwright, Locust/k6 (load), Sentry (runtime errors).
