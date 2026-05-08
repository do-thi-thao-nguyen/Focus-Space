// api.js
const API_BASE = "http://127.0.0.1:5000";

async function apiGet(path) {
  const res = await fetch(`${API_BASE}/${path}`);
  if (!res.ok) throw new Error(`GET ${path} failed`);
  return res.json();
}

async function apiPost(path, data) {
  const res = await fetch(`${API_BASE}/${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error(`POST ${path} failed`);
  return res.json();
}
