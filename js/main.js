// Dark mode toggle functionality
document.addEventListener('DOMContentLoaded', () => {
    const darkModeToggle = document.querySelector("#dark-mode-toggle");
    
    // Check for saved preference and apply immediately
    const isDarkMode = localStorage.getItem("darkMode") === "true";
    if (isDarkMode) {
        document.documentElement.classList.add("latex-dark");
    }
    
    // Toggle dark mode
    darkModeToggle.addEventListener('click', () => {
        document.documentElement.classList.toggle("latex-dark");
        const isDark = document.documentElement.classList.contains("latex-dark");
        localStorage.setItem("darkMode", isDark);
    });
}); 