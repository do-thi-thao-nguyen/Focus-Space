document.addEventListener("DOMContentLoaded", () => {
  const user = getCurrentUser();

  if (user) {
    const welcomeEl = document.getElementById("welcome");
    if (welcomeEl) welcomeEl.textContent = `Xin chào, ${user.username}`;

    const btnLogin = document.getElementById("btn_login");
    const btnRegister = document.getElementById("btn_register");
    const btnLogout = document.getElementById("btn_logout");

    if (btnLogin) btnLogin.classList.add("d-none");
    if (btnRegister) btnRegister.classList.add("d-none");
    if (btnLogout) btnLogout.classList.remove("d-none");

    if (btnLogout) {
      btnLogout.addEventListener("click", () => {
        logout();
      });
    }
  }
});
