const API_BASE = "http://127.0.0.1:5000"; // backend Flask

async function apiFetch(url, options = {}) {
  try {
    const res = await fetch(url, options);
    return await res.json();
  } catch (err) {
    console.error("Fetch error:", err);
  }
}


