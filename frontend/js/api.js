/**
 * StyleMirror API Client
 * Plain ES Module wrapper for backend FastAPI endpoints
 * Reference: stylemirror-docs/07_FRONTEND.md
 */

const BASE = "/v1";

async function request(path, options = {}) {
  const res = await fetch(BASE + path, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const errorMsg = data?.error?.message || (data?.detail?.error?.message) || "Request failed";
    const errorCode = data?.error?.code || (data?.detail?.error?.code) || "UNKNOWN_ERROR";
    const err = new Error(errorMsg);
    err.code = errorCode;
    throw err;
  }
  return data;
}

export const api = {
  styles: (type = "") => request(type ? `/styles?type=${type}` : "/styles"),
  uploadPhoto: (file) => {
    const f = new FormData();
    f.append("file", file);
    return request("/photos", { method: "POST", body: f });
  },
  generate: (body) =>
    request("/generations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  job: (id) => request(`/generations/${id}`),
  deletePhoto: (id) => request(`/photos/${id}`, { method: "DELETE" }),
};
