/**
 * StyleMirror API Client
 * Plain ES Module wrapper for backend FastAPI endpoints
 * Reference: stylemirror-docs/07_FRONTEND.md
 */

const BASE =
  typeof window !== "undefined" && window.location.port !== "8000" && window.location.protocol.startsWith("http")
    ? `${window.location.protocol}//${window.location.hostname}:8000/v1`
    : typeof window !== "undefined" && window.location.protocol === "file:"
    ? "http://127.0.0.1:8000/v1"
    : "/v1";

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(BASE + path, options);
  } catch (netErr) {
    const err = new Error(`Cannot connect to StyleMirror backend at ${BASE}. Please verify that uvicorn is running on port 8000.`);
    err.code = "NETWORK_ERROR";
    throw err;
  }

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const errorMsg =
      data?.error?.message ||
      (typeof data?.detail === "string" ? data.detail : data?.detail?.error?.message) ||
      data?.message ||
      `Request failed (HTTP ${res.status})`;
    const errorCode = data?.error?.code || (data?.detail?.error?.code) || "HTTP_ERROR";
    const err = new Error(errorMsg);
    err.code = errorCode;
    err.status = res.status;
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
