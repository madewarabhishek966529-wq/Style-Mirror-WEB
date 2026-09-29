# 08 — Security & Privacy

Face photos are sensitive biometric-adjacent data. Treat this as a first-class feature.

## Consent & Retention
- Consent checkbox before upload: "I agree to process my photo to generate previews."
- Checkbox: "This is my own photo."
- Photos private, signed URLs only, **auto-delete in 24 h**, instant delete button.
- **Never** use user photos for training; say so in the privacy policy.

## Compliance
- India: **DPDP Act 2023** — consent, purpose limitation, deletion on request, grievance contact.
- EU users: GDPR (facial images can be special-category data) — explicit consent, DPA with providers.
- Review the AI provider's data-retention/training terms; use a tier/setting that does not train on inputs.

## Abuse Prevention
- Rate limits per IP + session; daily cost cap per user.
- Keep provider safety filters on.
- Watermark shared images ("AI preview").
- Reject obvious minors where detectable; block multi-face photos.
- Don't market celebrity/public-figure editing.

## Application Security
- All AI calls server-side in Python; **API keys only in `backend/.env`** (or host secret manager). Never in HTML/JS, git history, logs or error responses.
- Rotate a key immediately if it is ever committed or shown; keep `.env` git-ignored.
- Enforce content-type, size and magic-byte checks on `POST /photos`.
- Use provider-side spend/quota limits on each API key, in addition to `DAILY_GENERATION_CAP`.
- Verify file magic bytes (not just extension); strip EXIF (incl. GPS) from stored images.
- CORS restricted to web origin; HTTPS only; security headers (CSP, HSTS).
- Logs: request metadata only, **no image content or face embeddings**.
- Delete face embeddings immediately after the identity check.

## Legal Pages Needed
Privacy Policy, Terms of Use, Cookie notice (if analytics), Contact/grievance email.
