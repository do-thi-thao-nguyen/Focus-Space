let selectedDevice = {};

function openDeviceModal(id, name, price) {
  selectedDevice = { id, name, price };
  document.getElementById("deviceId").value = id;
  document.getElementById("deviceName").value = name;
  document.getElementById("devicePrice").value = price;
  const modal = new bootstrap.Modal(document.getElementById("deviceModal"));
  modal.show();
}

async function addDevice() {
  const date = document.getElementById("deviceDate").value;
  const qty = parseInt(document.getElementById("deviceQty").value);
  const price = parseInt(document.getElementById("devicePrice").value);

  if (!date || qty <= 0) {
    alert("Vui lòng nhập đầy đủ thông tin!");
    return;
  }

  const payload = {
    type: "device",
    itemId: selectedDevice.id,
    name: selectedDevice.name,
    date,
    session: "full",   // mặc định thuê cả ngày
    guests: qty,       // dùng trường guests để lưu số lượng
    price: qty * price
  };

  const res = await apiFetch(`${API_BASE}/booking/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (res?.message) {
    alert("Đã thêm thiết bị vào giỏ hàng!");
    window.location.href = "booking.html";
  } else {
    alert("Không thể thêm thiết bị!");
  }
}
