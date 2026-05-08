let selectedVenueId = null;
let venuePrices = {};

// Mở modal
function openBookingModal(venueId, prices) {
  selectedVenueId = { id: venueId, name: "The Light House" };
  venuePrices = prices;
  const modal = new bootstrap.Modal(document.getElementById("bookingModal"));
  modal.show();
}

// Thêm Venue vào booking
async function addVenue() {
  const date = document.getElementById("bookingDate").value;
  const session = document.getElementById("bookingSession").value;
  const guests = parseInt(document.getElementById("guestCount").value);

  if (!date) {
    alert("Vui lòng chọn ngày thuê!");
    return;
  }

  // Tính giá theo buổi
  let price = 0;
  if (session === "morning") price = venuePrices.priceMorning;
  if (session === "afternoon") price = venuePrices.priceAfternoon;
  if (session === "full") price = venuePrices.priceFull;

  // Payload đầy đủ giống Postman test
  const payload = {
    type: "venue",
    itemId: selectedVenueId.id,
    name: selectedVenueId.name,
    date,
    session,
    guests,
    price
  };

  // Gọi API backend
  const res = await apiFetch(`${API_BASE}/booking/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (res?.message) {
    // Thành công → chuyển sang giỏ hàng
    window.location.href = "booking.html";
  } else {
    alert("Không thể thêm vào booking!");
  }
}
