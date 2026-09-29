# 07 — Frontend (HTML + CSS + JavaScript)

No framework, no bundler, no build step. Plain ES modules served as static files by FastAPI (or any static host).

## Pages
| File | Content |
|---|---|
| `index.html` | Landing: hero, before/after demo, how it works, FAQ, "Try Now" |
| `try.html` | Single page with 3 steps: Upload → Style → Result |
| `privacy.html`, `terms.html` | Legal |
| (P2) `looks.html`, `share.html` | Saved / shared looks |

## JS Modules (`frontend/js/`)
| Module | Responsibility |
|---|---|
| `api.js` | `fetch` wrapper for all endpoints, error mapping |
| `state.js` | Simple store object: `photoId`, `hairId`, `beardId`, `results[]` |
| `uploader.js` | Drag-drop, file picker, webcam (`getUserMedia`), client-side compress to ≤ 1600 px via `<canvas>` |
| `styleGrid.js` | Renders 25 hair + 25 beard cards, tabs, search, selection |
| `progress.js` | Generation progress text + polling loop |
| `slider.js` | Before/after comparison slider |
| `main.js` | Step navigation, wiring, consent check, delete button |

## Sections in `try.html`
1. **Consent + tips:** checkboxes "This is my own photo" and "I agree to photo processing" (required).
2. **Uploader:** preview, retake, validation messages.
3. **Style picker:** tabs Hairstyles / Beards, grid of cards, sticky bottom bar showing chosen hair + beard and a **Generate** button.
4. **Result:** big image, before/after slider, buttons Download / Try another / Change hair / Change beard / Delete my photo.

## Key Code Patterns

**API wrapper (`api.js`)**
```js
const BASE = "/v1";
async function request(path, options = {}) {
  const res = await fetch(BASE + path, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw Object.assign(new Error(data?.error?.message || "Request failed"), { code: data?.error?.code });
  return data;
}
export const api = {
  styles: (type) => request(`/styles?type=${type}`),
  uploadPhoto: (file) => { const f = new FormData(); f.append("file", file); return request("/photos", { method: "POST", body: f }); },
  generate: (body) => request("/generations", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
  job: (id) => request(`/generations/${id}`),
  deletePhoto: (id) => request(`/photos/${id}`, { method: "DELETE" }),
};
```

**Polling (`progress.js`)**
```js
export async function waitForJob(jobId, onStatus) {
  while (true) {
    const job = await api.job(jobId);
    onStatus(job.status);
    if (job.status === "done") return job.result_url;
    if (job.status === "failed") throw new Error(job.error || "Generation failed");
    await new Promise(r => setTimeout(r, 1500));
  }
}
```

**Before/after slider (`slider.js`)** — two stacked `<img>`; the top one clipped with `clip-path: inset(0 X% 0 0)` driven by an `<input type="range">`.

## Rules
- **Never put an API key in any JS/HTML file.** All AI calls go through the Python backend.
- Mobile-first CSS (flex/grid, `clamp()`, media queries). Test at 360 px width.
- No bare spinners; always show text: Analyzing face → Styling → Finishing.
- Show "Photo auto-deleted in 24 h" and the delete button at all times after upload.
- Actionable errors, e.g. "Face not clearly visible — face the camera in daylight."
- Accessibility: alt text, labels, keyboard focus, AA contrast, `prefers-reduced-motion`.
- Disable **Generate** until a photo is validated and at least one style is chosen.
- Use `loading="lazy"` on style thumbnails.
- CSS: variables in `:root` for colors/spacing; split into `base.css`, `layout.css`, `components.css`.

## Design Direction
Dark premium "barber shop" look: charcoal/navy background, one bright blue accent (like the reference sheets), large rounded image cards, subtle CSS transitions.

## Optional Analytics
Plain `fetch` calls to `/v1/events` (or PostHog snippet): `upload_started`, `validation_failed`, `style_selected`, `generate_clicked`, `generation_done`, `download_clicked`, `photo_deleted`.
