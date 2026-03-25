document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById("themeToggle");
    
    // Check the browser's local memory for a saved theme, default to light
    const savedTheme = localStorage.getItem("appTheme") || "light";

    // Apply the saved theme instantly
    if (savedTheme === "dark") {
        document.documentElement.setAttribute("data-theme", "dark");
        if (themeToggle) themeToggle.textContent = "☀️ Light Mode";
    }

    // Listen for button clicks to swap the theme
    if (themeToggle) {
        themeToggle.addEventListener("click", () => {
            const currentTheme = document.documentElement.getAttribute("data-theme");
            
            if (currentTheme === "dark") {
                document.documentElement.removeAttribute("data-theme");
                localStorage.setItem("appTheme", "light");
                themeToggle.textContent = "🌙 Dark Mode";
            } else {
                document.documentElement.setAttribute("data-theme", "dark");
                localStorage.setItem("appTheme", "dark");
                themeToggle.textContent = "☀️ Light Mode";
            }
        });
    }
});