document.addEventListener("DOMContentLoaded", async () => {
  // Lấy ID từ URL
  const urlParams = new URLSearchParams(window.location.search);
  const transactionId = urlParams.get("id");

  if (!transactionId) {
    alert("Không tìm thấy ID hóa đơn!");
    return;
  }

  let total = 0;

  try {
    // =============================
    // Gọi API lấy transaction (✅ thêm /booking cho khớp backend)
    // =============================
    const res = await apiFetch(`${API_BASE}/booking/transactions_venue/${transactionId}`);
    if (!res || res.error) {
      alert(res?.error || "Không tìm thấy hóa đơn!");
      return;
    }

    // =============================
    // Hiển thị thông tin khách hàng
    // =============================
    const customer = res.customer || {};
    document.getElementById("cusName").innerText = customer.name || "-";
    document.getElementById("cusEmail").innerText = customer.email || "-";
    document.getElementById("cusPhone").innerText = customer.phone || "-";
    document.getElementById("cusAddr").innerText = customer.address || "-";
    document.getElementById("cusNote").innerText = customer.note || "-";

    // =============================
    // Hiển thị Venue
    // =============================
    let venueRows = "";
    const venues = (res.items || []).filter(i => i.type === "venue");
    if (venues.length > 0) {
      venues.forEach(v => {
        total += v.price || 0;
        venueRows += `
          <tr>
            <td>${v.name}</td>
            <td>${v.date}</td>
            <td>${v.session === "morning" ? "Sáng" : v.session === "afternoon" ? "Chiều" : "Cả ngày"}</td>
            <td>${v.guests || "-"}</td>
            <td>${(v.price || 0).toLocaleString()} VND</td>
          </tr>`;
      });
    } else {
      venueRows = `<tr><td colspan="5" class="text-muted">Chưa có Venue</td></tr>`;
    }
    document.getElementById("venueSummary").innerHTML = venueRows;

    // =============================
    // Hiển thị Thiết bị
    // =============================
    let deviceRows = "";
    const devices = (res.items || []).filter(i => i.type === "device");
    if (devices.length > 0) {
      devices.forEach(d => {
        total += d.price || 0;
        deviceRows += `
          <tr>
            <td>${d.name}</td>
            <td>${d.date}</td>
            <td>${d.guests || d.qty || 1}</td>
            <td>${(d.price || 0).toLocaleString()} VND</td>
          </tr>`;
      });
    } else {
      deviceRows = `<tr><td colspan="4" class="text-muted">Chưa có Thiết bị</td></tr>`;
    }
    document.getElementById("deviceSummary").innerHTML = deviceRows;

    // =============================
    // Tổng cộng
    // =============================
    document.getElementById("transactionTotal").innerText = total.toLocaleString() + " VND";

    // =============================
    // Hàm block lịch & clear
    // =============================
    async function blockAndClear() {
      try {
        // ✅ chỉnh đúng endpoint block (thêm /booking)
        const res = await fetch(`${API_BASE}/booking/transactions_venue/block/${transactionId}`, { method: "POST" });
        if (!res.ok) {
          const err = await res.json();
          alert("❌ Block lịch lỗi: " + (err.error || "Unknown"));
          return false;
        }
        console.log("✅ Block lịch thành công!");

        // Clear localStorage
        localStorage.removeItem("invoiceCart");
        localStorage.removeItem("invoiceCustomer");
        return true;
      } catch (err) {
        console.error("❌ Lỗi block lịch:", err);
        return false;
      }
    }

    // =============================
    // Thanh toán MoMo
    // =============================
    const btnPayMoMo = document.getElementById("btnPayMoMo");
    if (btnPayMoMo) {
      btnPayMoMo.addEventListener("click", async () => {
        try {
          const res = await fetch(`${API_BASE}/momo/create_payment`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              amount: total,
              orderId: "order_" + Date.now(),
              orderInfo: "Thanh toán Venue & Thiết bị"
            }),
          });

          const data = await res.json();

          if (!res.ok || !data.payUrl) {
            alert("❌ Lỗi MoMo: " + (data.error || "Unknown"));
            return;
          }

          // Điều hướng sang MoMo
          window.location.href = data.payUrl;
        } catch (err) {
          console.error(err);
          alert("❌ Lỗi khi gọi API MoMo");
        }
      });
    }

    // Sau khi MoMo redirect về
    const params = new URLSearchParams(window.location.search);
    if (params.has("resultCode")) {
      const code = params.get("resultCode");
      if (code === "0") {
        alert("✅ Thanh toán MoMo thành công!");
        const ok = await blockAndClear();
        if (ok) window.location.href = "index.html";
      } else {
        alert("❌ Thanh toán thất bại, vui lòng thử lại.");
      }
    }

    // =============================
    // Thanh toán Tiền mặt
    // =============================
    const btnPayCash = document.getElementById("btnPayCash");
    const btnPrintCash = document.getElementById("btnPrintCash");

    if (btnPayCash) {
      btnPayCash.addEventListener("click", () => {
        const cashModal = new bootstrap.Modal(document.getElementById("cashModal"));
        cashModal.show();

        // Clear QR cũ
        const qrDiv = document.getElementById("qrcode");
        if (qrDiv) qrDiv.innerHTML = "";

        // Lấy transactionId từ URL
        const tid = new URLSearchParams(window.location.search).get("id");

        // Tạo link hóa đơn trực tiếp
        const invoiceUrl = `${window.location.origin}/transactions_venue.html?id=${tid}`;

        // Render QR code
        if (typeof QRCode !== "undefined") {
          QRCode.toCanvas(invoiceUrl, { width: 180 }, (err, canvas) => {
            if (err) {
              console.error("❌ Lỗi QR:", err);
              return;
            }
            qrDiv.appendChild(canvas);
          });
        } else {
          console.error("⚠️ Thư viện QRCode chưa được load!");
        }
      });
    }

    if (btnPrintCash) {
      btnPrintCash.addEventListener("click", async () => {
        window.print(); // In khung hóa đơn
        const ok = await blockAndClear();
        if (ok) {
          alert("✅ Thanh toán tiền mặt thành công!");
          window.location.href = "index.html";
        }
      });
    }

  } catch (err) {
    console.error("Lỗi khi load hóa đơn:", err);
    alert("Không thể tải hóa đơn!");
  }
});

if (btnPrintCash1) {
      btnPrintCash1.addEventListener("click", async () => {
        window.print(); // In khung hóa đơn
        
      });
    }
