document.addEventListener("DOMContentLoaded", () => {
  const tbody = document.getElementById("cartSummary");
  const totalEl = document.getElementById("transactionTotal");
  const btnPayCash = document.getElementById("btnPayCash");
  const btnPayMoMo = document.getElementById("btnPayMoMo");
  const btnPrintCash = document.getElementById("btnPrintCash");

  const cusNameEl = document.getElementById("cusName");
  const cusEmailEl = document.getElementById("cusEmail");
  const cusPhoneEl = document.getElementById("cusPhone");
  const cusAddrEl = document.getElementById("cusAddr");


  const API_BASE = "http://127.0.0.1:5000";
  const user = getCurrentUser();

  const cart = JSON.parse(localStorage.getItem("invoiceCart") || "[]");
  const customer = JSON.parse(localStorage.getItem("invoiceCustomer") || "{}");

  // render thông tin khách hàng
  cusNameEl.textContent = customer.name || "-";
  cusEmailEl.textContent = customer.email || "-";
  cusPhoneEl.textContent = customer.phone || "-";
  cusAddrEl.textContent = customer.address || "-";

  // ========================
  // render invoice
  // ========================
  function renderInvoice() {
    tbody.innerHTML = "";
    let total = 0;

    if (!cart.length) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-muted">Không có vé</td></tr>`;
      totalEl.textContent = "0 đ";
      return;
    }

    cart.forEach(item => {
      const price = item.qty * (item.price || 0);
      total += price;
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${item.seat}</td>
        <td>${item.ticket_type}</td>
        <td>${item.qty}</td>
        <td>${price.toLocaleString()} đ</td>
        <td>${item.date || "-"}</td>
        <td>${item.start_time || item.time || "-"}</td>
        <td>${item.end_time || "-"}</td>
      `;
      tbody.appendChild(tr);
    });

    totalEl.textContent = total.toLocaleString() + " đ";
  }

  // ========================
  // block ghế + clear cart
  // ========================
  async function blockSeatsAndClear() {
    for (const item of cart) {
      try {
        const payload = {
          seat: item.seat,
          date: item.date,
          start: `${item.date}T${item.start_time || item.time}:00`,
          end: `${item.date}T${item.end_time}:00`,
          ticket_type: item.ticket_type,
          qty: item.qty
        };

        const res = await fetch(`${API_BASE}/tickets/block`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
          const err = await res.json();
          alert(err.error || "❌ Block ghế lỗi");
        } else {
          console.log("✅ Block thành công:", payload);
        }
      } catch (err) {
        console.error("❌ Lỗi block ghế:", err);
      }
    }

    if (user?.id) {
      await fetch(`${API_BASE}/cart/${user.id}/clear`, { method: "POST" });
    }

    localStorage.removeItem("invoiceCart");
    localStorage.removeItem("invoiceCustomer");
  }

  // ========================
  // Thanh toán MoMo
  // ========================
  if (btnPayMoMo) {
    btnPayMoMo.addEventListener("click", async () => {
      try {
        const amount = cart.reduce((sum, item) => sum + item.qty * (item.price || 0), 0);

        const res = await fetch(`${API_BASE}/momo/create_payment`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            amount: amount,
            orderId: "order_" + Date.now(),
            orderInfo: "Thanh toán đặt chỗ Focus-Space"
          }),
        });

        const data = await res.json();

        if (!res.ok) {
          alert("❌ Lỗi MoMo: " + (data.error || "Unknown"));
          return;
        }

        if (data.payUrl) {
          window.location.href = data.payUrl;
        } else {
          alert("⚠️ Không nhận được link thanh toán từ MoMo");
        }
      } catch (err) {
        console.error(err);
        alert("❌ Lỗi khi gọi API MoMo");
      }
    });
  }

  // ========================
  // Check result MoMo sau redirect
  // ========================
  const params = new URLSearchParams(window.location.search);
  if (params.has("resultCode")) {
    const code = params.get("resultCode");
    if (code === "0") {
      alert("✅ Thanh toán MoMo thành công!");
      blockSeatsAndClear().then(() => {
        window.location.href = "index.html";
      });
    } else {
      alert("❌ Thanh toán thất bại, vui lòng thử lại.");
    }
  }

  if (btnPayCash) {
  btnPayCash.addEventListener("click", () => {
    const cashModal = new bootstrap.Modal(document.getElementById("cashModal"));
    cashModal.show();

    // Clear QR cũ
    const qrDiv = document.getElementById("qrcode");
    qrDiv.innerHTML = "";

    // Lấy transactionId từ URL
    const transactionId = new URLSearchParams(window.location.search).get("id");

    // Tạo link hóa đơn trực tiếp
    const invoiceUrl = `${window.location.origin}/transactions_venue.html?id=${transactionId}`;

    // Render QR code dẫn thẳng tới hóa đơn
    QRCode.toCanvas(document.createElement("canvas"), invoiceUrl, { width: 180 }, (err, canvas) => {
      if (err) console.error(err);
      qrDiv.appendChild(canvas);
    });
  });
}

// In chỉ khung hóa đơn
if (btnPrintCash) {
  btnPrintCash.addEventListener("click", async () => {
    // In chỉ phần hóa đơn
    const invoice = document.getElementById("invoice").innerHTML;
    const win = window.open("", "", "height=700,width=900");
    win.document.write(`
      <html>
        <head>
          <title>Hóa đơn</title>
          <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h2 { text-align: center; margin-bottom: 20px; }
          </style>
        </head>
        <body>
          ${invoice}
        </body>
      </html>
    `);
    win.document.close();
    win.print();

    // Sau khi in xong: block ghế + clear cart + redirect về trang chủ
    await blockSeatsAndClear();
    window.location.href = "index.html";
  });
}


  renderInvoice();
});
if (btnPrintCash1) {
  btnPrintCash1.addEventListener("click", async () => {
    // In chỉ phần hóa đơn
    const invoice = document.getElementById("invoice").innerHTML;
    const win = window.open("", "", "height=700,width=900");
    win.document.write(`
      <html>
        <head>
          <title>Hóa đơn</title>
          <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h2 { text-align: center; margin-bottom: 20px; }
          </style>
        </head>
        <body>
          ${invoice}
        </body>
      </html>
    `);
    win.document.close();
    win.print();
   });
};