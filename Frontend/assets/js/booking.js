document.addEventListener("DOMContentLoaded", async () => {
  const items = await apiFetch(`${API_BASE}/booking/`);
  if (!items) return;

  let venueRows = "";
  let deviceRows = "";
  let total = 0;

  items.forEach(i => {
    total += i.price || 0;

    if (i.type === "venue") {
      venueRows += `
        <tr>
          <td>${i.name || "-"}</td>
          <td>${i.date || "-"}</td>
          <td>${
            i.session === "morning"
              ? "Sáng"
              : i.session === "afternoon"
              ? "Chiều"
              : i.session === "full"
              ? "Cả ngày"
              : "-"
          }</td>
          <td>${i.guests || "-"}</td>
          <td>${(i.price || 0).toLocaleString()} VND</td>
          <td>
            <button onclick="removeItem('${i._id}')" class="btn btn-sm btn-danger">
              <i class="bi bi-x-circle"></i> Xóa
            </button>
          </td>
        </tr>`;
    } else if (i.type === "device") {
      deviceRows += `
        <tr>
          <td>${i.name || "-"}</td>
          <td>${i.guests || "-"}</td>
          <td>${i.date || "-"}</td>
          <td>Cả ngày</td>
          <td>${(i.price || 0).toLocaleString()} VND</td>
          <td>
            <button onclick="removeItem('${i._id}')" class="btn btn-sm btn-danger">
              <i class="bi bi-x-circle"></i> Xóa
            </button>
          </td>
        </tr>`;
    }
  });

  document.getElementById("booking-venue-list").innerHTML = venueRows;
  document.getElementById("booking-device-list").innerHTML = deviceRows;
  document.getElementById("booking-total").innerText =
    total.toLocaleString() + " VND";
});

async function removeItem(id) {
  const data = await apiFetch(`${API_BASE}/booking/${id}`, { method: "DELETE" });
  if (data?.message) location.reload();
}

async function clearCart() {
  if (!confirm("Bạn có chắc muốn xóa toàn bộ giỏ hàng?")) return;

  try {
    const res = await apiFetch(`${API_BASE}/booking/clear`, { method: "DELETE" });
    if (res?.message) {
      alert("🗑️ Giỏ hàng đã được xóa!");
      location.reload();
    } else {
      alert("❌ Không thể xóa giỏ hàng!");
    }
  } catch (err) {
    console.error("❌ Lỗi clear cart:", err);
    alert("Không kết nối được server!");
  }
}


async function checkoutBooking() {
  // Lấy dữ liệu trong booking
  const items = await apiFetch(`${API_BASE}/booking/`);
  if (!items || items.length === 0) {
    alert("Giỏ hàng đang trống!");
    return;
  }

  // Tính tổng
  let total = 0;
  items.forEach(i => total += i.price || 0);

  // Chuẩn bị payload giao dịch
  const payload = {
    items,
    total,
    customer: {
      name: "Khách vãng lai",
      email: "guest@example.com",
      phone: "0000000000"
    }
  };

  // Gửi sang transaction_booking
  const res = await apiFetch(`${API_BASE}/transaction_booking/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (res?.message) {
    alert("Thanh toán thành công!");
    // Xóa giỏ hàng sau khi thanh toán
    await apiFetch(`${API_BASE}/booking/clear`, { method: "DELETE" });
    window.location.href = "transactions.html";
  } else {
    alert("Thanh toán thất bại!");
  }
}
async function checkoutBooking() {
  const customer = {
    name: document.getElementById("cusName")?.value || "",
    email: document.getElementById("cusEmail")?.value || "",
    phone: document.getElementById("cusPhone")?.value || "",
    address: document.getElementById("cusAddr")?.value || "",
    note: document.getElementById("cusNote")?.value || ""
  };

  const res = await apiFetch(`${API_BASE}/booking/checkout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(customer)
  });

  if (res?.transactionId) {
    window.location.href = `transactions_venue.html?id=${res.transactionId}`;
  } else {
    console.error("Checkout response:", res);
    alert("Không thể khởi tạo thanh toán!");
  }
}
