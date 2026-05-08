document.addEventListener("DOMContentLoaded", async () => {
  await loadHistory();

  const btnFilter = document.getElementById("btnFilter");
  const btnReset = document.getElementById("btnReset");

  if (btnFilter) {
    btnFilter.addEventListener("click", () => {
      const date = document.getElementById("filterDate")?.value || "";
      const session = document.getElementById("filterSession")?.value || "";
      loadHistory(date, session);
    });
  }

  if (btnReset) {
    btnReset.addEventListener("click", () => {
      const dateInput = document.getElementById("filterDate");
      const sessionInput = document.getElementById("filterSession");
      if (dateInput) dateInput.value = "";
      if (sessionInput) sessionInput.value = "";
      loadHistory();
    });
  }
});

async function loadHistory(date = "", session = "") {
  let url = `${API_BASE}/history`;
  const params = [];
  if (date) params.push(`date=${date}`);
  if (session) params.push(`session=${session}`);
  if (params.length > 0) url += "?" + params.join("&");

  try {
    const res = await fetch(url);
    const data = await res.json();

    let rows = "";
    if (Array.isArray(data) && data.length > 0) {
      data.forEach(v => {
        rows += `
          <tr>
            <td>${v.item}</td>
            <td>${v.date}</td>
            <td>
              ${v.session === "morning" ? "Sáng" :
                v.session === "afternoon" ? "Chiều" : "Cả ngày"}
            </td>
          </tr>`;
      });
    } else {
      rows = `<tr><td colspan="3" class="text-muted">Không có dữ liệu</td></tr>`;
    }

    const tbody = document.getElementById("historyBody");
    if (tbody) tbody.innerHTML = rows;
  } catch (err) {
    console.error("❌ Lỗi khi load dữ liệu:", err);
  }
}
