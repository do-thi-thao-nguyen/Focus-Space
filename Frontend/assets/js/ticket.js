document.addEventListener("DOMContentLoaded", () => {
  const API_BASE = "http://127.0.0.1:5000";
  const user = getCurrentUser();
  if (!user) {
    alert("Bạn cần đăng nhập trước khi đặt vé!");
    window.location.href = "index.html";
    return;
  }

  const seatInput = document.getElementById("selectedSeat");
  const ticketType = document.getElementById("ticketType");
  const ticketQty = document.getElementById("ticketQty");
  const ticketDate = document.getElementById("ticketDate");
  const ticketTime = document.getElementById("ticketTime");
  const btnAddToCart = document.getElementById("btnAddToCart");

  let selectedSeat = null;

  // Auto-fill ngày giờ
  const now = new Date();
  if (now.getHours() >= 17 && now.getMinutes() >= 30) {
    now.setDate(now.getDate() + 1);
    now.setHours(9, 0, 0, 0);
  }
  ticketDate.value = now.toISOString().split("T")[0];
  ticketTime.value = now.toTimeString().slice(0, 5);

  // Load trạng thái ghế
  async function loadSeatStatus() {
    const date = ticketDate.value;
    const time = ticketTime.value;
    const res = await fetch(`${API_BASE}/tickets/status_all?date=${date}&time=${time}`);
    const data = await res.json();
    if (res.ok) {
      const map = {};
      data.forEach(item => map[item.seat] = item.status);
      applySeatStatus(map);
    }
  }

  function applySeatStatus(map) {
    document.querySelectorAll(".seat").forEach(seatEl => {
      const seatId = seatEl.textContent.trim();
      const status = map[seatId] || "available";
      seatEl.dataset.seat = seatId;
      seatEl.classList.remove("available", "selected", "booked");
      seatEl.classList.add(status);

      seatEl.onclick = () => {
        if (seatEl.classList.contains("booked")) {
          alert(`❌ Ghế ${seatId} đã được đặt!`);
          return;
        }
        document.querySelectorAll(".seat").forEach(s => s.classList.remove("selected"));
        seatEl.classList.add("selected");
        selectedSeat = seatId;
        seatInput.value = selectedSeat;
        new bootstrap.Modal(document.getElementById("ticketModal")).show();
      };
    });
  }

  // Thêm vào giỏ
  btnAddToCart.addEventListener("click", async () => {
    if (!selectedSeat) {
      alert("Vui lòng chọn ghế!");
      return;
    }
    const type = ticketType.value;
    const qty = parseInt(ticketQty.value, 10) || 1;
    const date = ticketDate.value;
    const time = ticketTime.value;
    const prices = { "1hour": 30000, "4hour": 80000, "student": 60000, "combo": 135000 };
    const price = prices[type] * qty;

    const res = await fetch(`${API_BASE}/cart/${user.id}/add`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ seat: selectedSeat, ticket_type: type, qty, date, time, price })
    });
    if (!res.ok) {
      alert("❌ Không thể thêm vào giỏ");
      return;
    }
    alert(`✅ Đã thêm ${qty} vé cho ghế ${selectedSeat}`);
    bootstrap.Modal.getInstance(document.getElementById("ticketModal")).hide();
    loadSeatStatus();
  });

  loadSeatStatus();
  setInterval(loadSeatStatus, 60000);
});
