/**
 * API client for PulseGuard backend.
 *
 * Uses RELATIVE paths ("/api/...") so that:
 *  - In Docker: NGINX reverse-proxy handles /api/ → backend:8000/api/
 *  - In local dev: Vite dev-server proxy handles /api/ → localhost:8000/api/
 *
 * This eliminates the VITE_API_BASE_URL="" empty-string bypass bug.
 */

async function handleResponse(response) {
  if (!response.ok) {
    let errorMsg = `HTTP Error ${response.status}`;
    try {
      const errData = await response.json();
      if (errData.detail) errorMsg = errData.detail;
    } catch (_) {}
    throw new Error(errorMsg);
  }
  if (response.status === 204) return null;
  return response.json();
}

export async function fetchUrls() {
  return handleResponse(await fetch("/api/urls"));
}

export async function addUrl(url, name = "") {
  const body = { url };
  if (name && name.trim()) body.name = name.trim();
  return handleResponse(
    await fetch("/api/urls", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
  );
}

export async function deleteUrl(id) {
  return handleResponse(await fetch(`/api/urls/${id}`, { method: "DELETE" }));
}

export async function fetchUrlChecks(id, limit = 30) {
  return handleResponse(await fetch(`/api/urls/${id}/checks?limit=${limit}`));
}

export async function fetchUrlDetail(id) {
  return handleResponse(await fetch(`/api/urls/${id}`));
}
