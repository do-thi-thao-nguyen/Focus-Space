document.addEventListener("DOMContentLoaded", () => {
  const API_BASE = "http://127.0.0.1:5000";
  const user = getCurrentUser();
  if (!user) {
    alert("Bạn cần đăng nhập trước!");
    window.location.href = "index.html";
    return;
  }

  const cartBody = document.getElementById("cartBody");
  const cartTotal = document.getElementById("cartTotal");
  const btnClearCart = document.getElementById("btnClearCart");
  const btnCheckout = document.getElementById("btnCheckout");

  // Input khách hàng
  const cusNameInput = document.getElementById("cusNameInput");
  const cusEmailInput = document.getElementById("cusEmailInput");
  const cusPhoneInput = document.getElementById("cusPhoneInput");
  const cusAddrInput = document.getElementById("cusAddrInput");

  let currentCart = [];

  // ========================
  // Load giỏ hàng từ backend
  // ========================
  async function loadCart() {
    try {
      const res = await fetch(`${API_BASE}/cart/${user.id}`);
      const data = await res.json();

      currentCart = data.items || [];
      cartBody.innerHTML = "";
      let total = 0;

      if (!currentCart.length) {
        cartBody.innerHTML = `<tr><td colspan="7" class="text-muted">Giỏ hàng trống</td></tr>`;
        cartTotal.textContent = "0 đ";
        return;
      }

      currentCart.forEach(item => {
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
          <td>
            <button class="btn btn-sm btn-danger btnRemove" data-id="${item._id}">Xóa</button>
          </td>
        `;
        cartBody.appendChild(tr);
      });

      cartTotal.textContent = total.toLocaleString() + " đ";

      // Sự kiện xóa item
      document.querySelectorAll(".btnRemove").forEach(btn => {
        btn.addEventListener("click", async () => {
          const id = btn.dataset.id;
          await fetch(`${API_BASE}/cart/${user.id}/remove`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id })
          });
          loadCart();
        });
      });

    } catch (err) {
      console.error("❌ Lỗi load cart:", err);
    }
  }

  // ========================
  // Hàm thêm vào giỏ (dùng từ ticket.js)
  // ========================
  window.addToCart = async function (item) {
    try {
      const res = await fetch(`${API_BASE}/cart/${user.id}/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(item)
      });
      const data = await res.json();

      if (!res.ok) {
        // ❌ Nếu lỗi (vd: trùng giờ ghế) thì chỉ hiện thông báo
        alert(data.error || "❌ Không thể thêm vào giỏ");
        return;
      }

      // ✅ Nếu thành công mới load lại giỏ
      alert("✅ Đã thêm vào giỏ hàng");
      loadCart();
    } catch (err) {
      console.error("❌ Lỗi khi thêm vào giỏ:", err);
      alert("❌ Lỗi kết nối server");
    }
  };

  // ========================
  // Xóa toàn bộ giỏ hàng
  // ========================
  if (btnClearCart) {
    btnClearCart.addEventListener("click", async () => {
      if (!confirm("Bạn có chắc muốn xóa toàn bộ giỏ hàng?")) return;

      await fetch(`${API_BASE}/cart/${user.id}/clear`, { method: "POST" });
      loadCart();
    });
  }

  // ========================
  // Thanh toán -> lưu vào localStorage
  // ========================
  if (btnCheckout) {
    btnCheckout.addEventListener("click", () => {
      if (!currentCart.length) {
        alert("❌ Giỏ hàng trống!");
        return;
      }

      // Lưu thông tin khách hàng
      const customer = {
        name: cusNameInput.value.trim(),
        email: cusEmailInput.value.trim(),
        phone: cusPhoneInput.value.trim(),
        address: cusAddrInput.value.trim(),
      };

      localStorage.setItem("invoiceCustomer", JSON.stringify(customer));
      localStorage.setItem("invoiceCart", JSON.stringify(currentCart));

      // Điều hướng sang trang hóa đơn
      window.location.href = "transactions.html";
    });
  }

  loadCart();
});
