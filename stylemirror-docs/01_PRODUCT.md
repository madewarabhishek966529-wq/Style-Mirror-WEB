# 01 — Product

## Name
StyleMirror (working title)

## Problem
Men can't preview how a haircut or beard will look before visiting the barber.

## Solution
User uploads one clear selfie. System generates realistic previews of the user's own face with any of 25 hairstyles and 25 beard styles, alone or combined.

## Target Users
Men 16–45; barbers/salons later (B2B).

## Core Value
Identity-preserving result: still looks like *you*, only hair/beard changes.

## Scope

### MVP (Phase 1)
- Upload / webcam capture selfie
- Photo validation (one face, frontal, good light, sharp)
- Browse 25 hairstyles + 25 beards
- Generate: hair only, beard only, or hair + beard combo
- Before/after slider
- Download / share
- Anonymous usage, photos auto-deleted in 24 h, manual delete button

### Phase 2
- Google login, saved looks
- "Suggest for me" (top 6 by face shape)
- Hair color change
- Compare up to 4 looks
- Side/back view (beta)

### Phase 3
- Barber mode (share look via link/QR)
- Premium plan (HD, unlimited)
- Women's styles, bigger catalog
- Flutter mobile app on same backend

### Out of Scope
Video try-on, live AR camera, e-commerce, salon booking.

## User Flow
```
Landing → Upload Photo → Photo Check → Choose Style(s) → Generating → Result → Try another / Download / Share
```
1. **Landing:** headline, before/after demo, "Try Now".
2. **Upload:** drag-drop, picker, or webcam. Tips: face front, no cap/glasses, good light.
3. **Photo check (server):** exactly one face, face ≥ 30% of frame, not blurry, not dark, yaw < 20°. On fail → actionable error.
4. **Style picker:** tabs Hairstyles / Beards, 25 cards each. Select max 1 hair + 1 beard.
5. **Generate:** progress text; target < 15 s.
6. **Result:** big image, before/after slider, change hair, change beard, download, share, regenerate.
7. **Delete:** "Delete my photo now" always visible.
