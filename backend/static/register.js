document.getElementById("registerForm").addEventListener("submit", function(event) {

    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;
    const errorMsg = document.getElementById("errorMsg");

    errorMsg.textContent = "";

    if (password.length < 6) {
        event.preventDefault();
        errorMsg.textContent = "Password must be at least 6 characters long.";
        return;
    }

    if (password !== confirmPassword) {
        event.preventDefault();
        errorMsg.textContent = "Passwords do not match.";
        return;
    }
});