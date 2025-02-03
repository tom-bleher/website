// Dark mode toggle functionality
document.addEventListener('DOMContentLoaded', () => {
    const darkModeToggle = document.querySelector("#dark-mode-toggle");
    
    // Create overlay element
    const overlay = document.createElement('div');
    overlay.className = 'theme-transition-overlay';
    document.body.appendChild(overlay);
    
    // Check for saved preference and apply immediately
    const isDarkMode = localStorage.getItem("darkMode") === "true";
    if (isDarkMode) {
        document.documentElement.classList.add("latex-dark");
    }
    
    // Toggle dark mode with transition
    darkModeToggle.addEventListener('click', () => {
        // Get the click position relative to viewport
        const rect = darkModeToggle.getBoundingClientRect();
        const clickX = rect.left + rect.width / 2;
        const clickY = rect.top + rect.height / 2;
        
        // Calculate the maximum distance to a corner
        const maxDistance = Math.max(
            Math.hypot(clickX, clickY),
            Math.hypot(window.innerWidth - clickX, clickY),
            Math.hypot(clickX, window.innerHeight - clickY),
            Math.hypot(window.innerWidth - clickX, window.innerHeight - clickY)
        );
        
        // Apply the transition
        overlay.style.transition = `opacity ${getComputedStyle(document.documentElement).getPropertyValue('--transition-duration')}`;
        overlay.classList.add('active');
        
        // Toggle dark mode after a small delay
        setTimeout(() => {
            document.documentElement.classList.toggle("latex-dark");
            const isDark = document.documentElement.classList.contains("latex-dark");
            localStorage.setItem("darkMode", isDark);
            
            // Remove overlay
            overlay.classList.remove('active');
        }, 50);
    });
}); 