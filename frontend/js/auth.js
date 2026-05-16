const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const errorMsg = document.getElementById("error-msg");

if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (res.ok) {
        window.location.href = "index.html"; // Go back to map
      } else {
        const data = await res.json();
        errorMsg.innerText = data.error || "Login Failed";
      }
    } catch (err) {
      errorMsg.innerText = "Network Error";
    }
  });
}

if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
      const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });

      if (res.ok) {
        window.location.href = "index.html"; // Go back to map
      } else {
        const data = await res.json();
        errorMsg.innerText = data.error || "Registration Failed";
      }
    } catch (err) {
      errorMsg.innerText = "Network Error";
    }
  });
}
