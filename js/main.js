// Dark mode toggle functionality
document.addEventListener('DOMContentLoaded', () => {
    const darkModeToggle = document.querySelector("#dark-mode-toggle");
    
    // Check for saved preference and apply immediately
    const isDarkMode = localStorage.getItem("darkMode") === "true";
    if (isDarkMode) {
        document.body.classList.add("latex-dark");
    }
    
    // Toggle dark mode
    darkModeToggle.addEventListener('click', () => {
        document.body.classList.toggle("latex-dark");
        const isDark = document.body.classList.contains("latex-dark");
        localStorage.setItem("darkMode", isDark);
    });
}); 