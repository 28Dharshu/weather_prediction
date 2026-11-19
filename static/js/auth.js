document.addEventListener("DOMContentLoaded", () => {
    // -------------------------------------------------------------
    // Login Form Handler
    // -------------------------------------------------------------
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            clearErrors();

            const username = loginForm.username.value.trim();
            const password = loginForm.password.value;
            const submitBtn = loginForm.querySelector("button[type='submit']");

            // Client-side quick check
            let hasError = false;
            if (!username) {
                showFieldError("username", "Please enter username.");
                hasError = true;
            }
            if (!password) {
                showFieldError("password", "Please enter your password.");
                hasError = true;
            }
            if (hasError) return;

            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';

            const res = await API.post("/api/auth/login", { username, password });

            if (res.ok && res.data.success) {
                showAlert("Login successful! Redirecting...", "success");
                setTimeout(() => {
                    window.location.href = "/dashboard";
                }, 800);
            } else {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Sign In';

                if (res.data.errors) {
                    for (const [field, msg] of Object.entries(res.data.errors)) {
                        showFieldError(field, msg);
                    }
                } else {
                    showAlert(res.data.error || "Login failed. Please check credentials.", "danger");
                }
            }
        });
    }

    // -------------------------------------------------------------
    // Register Form Handler
    // -------------------------------------------------------------
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            clearErrors();

            const username = registerForm.username.value.trim();
            const email = registerForm.email.value.trim();
            const password = registerForm.password.value;
            const confirm_password = registerForm.confirm_password.value;
            const location = registerForm.location.value.trim();
            const submitBtn = registerForm.querySelector("button[type='submit']");

            // Client-side quick validation
            let hasError = false;
            if (!username) {
                showFieldError("username", "Please enter a username.");
                hasError = true;
            }
            if (!email) {
                showFieldError("email", "Please enter an email.");
                hasError = true;
            }
            if (!password) {
                showFieldError("password", "Please enter a password.");
                hasError = true;
            } else if (password.length < 6) {
                showFieldError("password", "Password must have at least 6 characters.");
                hasError = true;
            }
            if (!confirm_password) {
                showFieldError("confirm_password", "Please confirm password.");
                hasError = true;
            } else if (password !== confirm_password) {
                showFieldError("confirm_password", "Password did not match.");
                hasError = true;
            }
            if (!location) {
                showFieldError("location", "Please enter your location.");
                hasError = true;
            }
            if (hasError) return;

            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating account...';

            const res = await API.post("/api/auth/register", {
                username,
                email,
                password,
                confirm_password,
                location
            });

            if (res.ok && res.data.success) {
                showAlert("Account created successfully! Redirecting to login...", "success");
                setTimeout(() => {
                    window.location.href = "/login";
                }, 1200);
            } else {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Create Account';

                if (res.data.errors) {
                    for (const [field, msg] of Object.entries(res.data.errors)) {
                        showFieldError(field, msg);
                    }
                } else {
                    showAlert(res.data.error || "Registration failed.", "danger");
                }
            }
        });
    }

    function showFieldError(fieldName, msg) {
        const errorElem = document.getElementById(`${fieldName}_error`);
        if (errorElem) {
            errorElem.innerText = msg;
            errorElem.style.display = "block";
        }
    }

    function clearErrors() {
        document.querySelectorAll(".error-feedback").forEach(el => {
            el.innerText = "";
            el.style.display = "none";
        });
        const alertEl = document.getElementById("alertBox");
        if (alertEl) alertEl.style.display = "none";
    }

    function showAlert(msg, type = "danger") {
        const alertEl = document.getElementById("alertBox");
        if (alertEl) {
            alertEl.className = `alert alert-${type}`;
            alertEl.innerText = msg;
            alertEl.style.display = "block";
        }
    }
});
