let selectedVenueId = null;
let venuePrices = {};

function openBookingModal(venueId, prices) {
  selectedVenueId = { id: venueId, name: "The Nest" };
  venuePrices = prices;
  const modal = new bootstrap.Modal(document.getElementById("bookingModal"));
  modal.show();
}

async function addVenue() {
  const date = document.getElementById("bookingDate").value;
  const session = document.getElementById("bookingSession").value;
  const guests = parseInt(document.getElementById("guestCount").value);

  if (!date) {
    alert("Vui lòng chọn ngày thuê!");
    return;
  }

  let price = 0;
  if (session === "morning") price = venuePrices.priceMorning;
  if (session === "afternoon") price = venuePrices.priceAfternoon;
  if (session === "full") price = venuePrices.priceFull;

  const payload = {
    type: "venue",
    itemId: selectedVenueId.id,
    name: selectedVenueId.name,
    date,
    session,
    guests,
    price
  };

  const res = await apiFetch(`${API_BASE}/booking/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (res?.message) {
    window.location.href = "booking.html";
  } else {
    alert("Không thể thêm vào booking!");
  }
}
