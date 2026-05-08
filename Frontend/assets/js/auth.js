

// Hiện alert thông báo
function showAlert(message, type = "success") {
  const alertBox = document.getElementById("alertBox");
  if (!alertBox) {
    alert(message);
    return;
  }
  alertBox.textContent = message;
  alertBox.className = `alert alert-${type} position-fixed top-0 start-50 translate-middle-x mt-3`;
  alertBox.classList.remove("d-none");
  setTimeout(() => alertBox.classList.add("d-none"), 3000);
}

// Lưu user
function saveUser(user) {
  localStorage.setItem("current_user", JSON.stringify(user));
}


// Lấy user hiện tại
function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem("current_user"));
  } catch {
    return null;
  }
}

// Đăng nhập
async function login(username, password) {
  const res = await fetch(`${API_BASE}/users/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  if (!res.ok) throw data.error || "Lỗi đăng nhập";

  saveUser(data.user);
  showAlert("Đăng nhập thành công!", "success");
  return data.user;
}

// Đăng ký
async function register(data) {
  const res = await fetch(`${API_BASE}/users/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  const json = await res.json();
  if (!res.ok) throw json.error || "Lỗi đăng ký";

  showAlert("Đăng ký thành công!", "success");
  return json;
}

// Đăng xuất
function logout() {
  localStorage.removeItem("current_user");
  showAlert("Đã đăng xuất", "info");
  location.reload();
}

// Khởi tạo sự kiện
document.addEventListener("DOMContentLoaded", () => {
  const user = getCurrentUser();

  if (user) {
    const welcome = document.getElementById("welcome");
    if (welcome) welcome.textContent = `Xin chào, ${user.username}`;

    const btnLogin = document.getElementById("btn_login");
    const btnRegister = document.getElementById("btn_register");
    const btnLogout = document.getElementById("btn_logout");

    if (btnLogin) btnLogin.classList.add("d-none");
    if (btnRegister) btnRegister.classList.add("d-none");
    if (btnLogout) btnLogout.classList.remove("d-none");
  }

  // Login
  document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const u = document.getElementById("loginUsername").value;
      const p = document.getElementById("loginPassword").value;
      await login(u, p);
      location.reload();
    } catch (err) {
      showAlert(err, "danger");
    }
  });

  // Register
  document.getElementById("registerForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const data = {
        username: document.getElementById("regUsername").value,
        password: document.getElementById("regPassword").value,
        fullname: document.getElementById("regFullname").value,
        email: document.getElementById("regEmail").value,
      };
      await register(data);
      document.getElementById("registerModal").querySelector(".btn-close").click();
      showAlert("Vui lòng đăng nhập để tiếp tục", "info");
    } catch (err) {
      showAlert(err, "danger");
    }
  });

  // Logout
  document.getElementById("btn_logout")?.addEventListener("click", logout);
});

