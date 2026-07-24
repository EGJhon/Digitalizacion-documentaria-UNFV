// Verificar si está en una página protegida y no tiene token
const token = localStorage.getItem("unfv_token");
const currentPath = window.location.pathname;

if(currentPath.includes("dashboard.html") && !token) {
    window.location.href = "login.html";
}

// Login
const loginForm = document.getElementById("loginForm");
if(loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;
        const errorMsg = document.getElementById("errorMsg");
        
        try {
            const res = await fetch("/api/v1/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });
            
            if(res.ok) {
                const data = await res.json();
                localStorage.setItem("unfv_token", data.token);
                if (data.role_id) localStorage.setItem("unfv_role_id", data.role_id);
                if (data.username) localStorage.setItem("unfv_username", data.username);
                if (data.user_id) localStorage.setItem("unfv_user_id", data.user_id);
                window.location.href = "dashboard.html";
            } else {
                errorMsg.textContent = "Credenciales incorrectas";
                errorMsg.style.display = "block";
            }
        } catch (error) {
            errorMsg.textContent = "Error de conexión al servidor";
            errorMsg.style.display = "block";
        }
    });
}

// Logout
const btnLogout = document.getElementById("btnLogout");
if(btnLogout) {
    btnLogout.addEventListener("click", (e) => {
        e.preventDefault();
        localStorage.removeItem("unfv_token");
        localStorage.removeItem("unfv_role_id");
        localStorage.removeItem("unfv_username");
        localStorage.removeItem("unfv_user_id");
        window.location.href = "login.html";
    });
}
