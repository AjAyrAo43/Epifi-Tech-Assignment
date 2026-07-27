const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function handleResponse(response) {
  if (!response.ok) {
    let errorMsg = `HTTP Error ${response.status}`;
    try {
      const errData = await response.json();
      if (errData.detail) {
        errorMsg = errData.detail;
      }
    } catch (_) {}
    throw new Error(errorMsg);
  }
  if (response.status === 204) {
    return null;
  }
  return await response.json();
}

export async function fetchUrls() {
  const response = await fetch(`${API_BASE_URL}/api/urls`);
  return handleResponse(response);
}

export async function addUrl(url) {
  const response = await fetch(`${API_BASE_URL}/api/urls`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
  return handleResponse(response);
}

export async function deleteUrl(id) {
  const response = await fetch(`${API_BASE_URL}/api/urls/${id}`, {
    method: 'DELETE',
  });
  return handleResponse(response);
}

export async function fetchUrlChecks(id, limit = 20) {
  const response = await fetch(`${API_BASE_URL}/api/urls/${id}/checks?limit=${limit}`);
  return handleResponse(response);
}
