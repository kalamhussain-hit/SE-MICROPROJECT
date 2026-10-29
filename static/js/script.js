/**
 * Smart Lost & Found Portal for Campus
 * Client-Side Logic & Enhancements
 */

document.addEventListener('DOMContentLoaded', () => {
    // -----------------------------------------------------------------------
    // Mobile Navigation Bar Toggle
    // -----------------------------------------------------------------------
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('open');
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('open');
            }
        });
    }

    // -----------------------------------------------------------------------
    // Flash Notifications Auto-Dismiss (after 6 seconds)
    // -----------------------------------------------------------------------
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach((alert) => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 500);
        }, 6000);
    });

    // -----------------------------------------------------------------------
    // Registration Form Validation
    // -----------------------------------------------------------------------
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            const password = document.getElementById('reg-password')?.value;
            const confirm = document.getElementById('reg-confirm-password')?.value;
            const email = document.getElementById('reg-email')?.value?.trim();

            if (password && password.length < 6) {
                e.preventDefault();
                alert('Password must be at least 6 characters long.');
                return;
            }

            if (password !== confirm) {
                e.preventDefault();
                alert('Password and Confirm Password do not match. Please verify.');
                return;
            }

            const emailRegex = /^[\w\.-]+@[\w\.-]+\.\w+$/;
            if (email && !emailRegex.test(email)) {
                e.preventDefault();
                alert('Please enter a valid email address.');
                return;
            }
        });
    }

    // -----------------------------------------------------------------------
    // Report Item Form Validation
    // -----------------------------------------------------------------------
    const reportForm = document.getElementById('reportItemForm');
    if (reportForm) {
        reportForm.addEventListener('submit', (e) => {
            const title = document.getElementById('item-title')?.value?.trim();
            const description = document.getElementById('item-description')?.value?.trim();
            const location = document.getElementById('item-location')?.value?.trim();
            const dateVal = document.getElementById('item-date')?.value;

            if (!title || title.length < 3) {
                e.preventDefault();
                alert('Item title must be at least 3 characters.');
                return;
            }

            if (!description || description.length < 10) {
                e.preventDefault();
                alert('Please enter a descriptive explanation of at least 10 characters.');
                return;
            }

            if (!location || location.length < 3) {
                e.preventDefault();
                alert('Please specify an accurate campus location.');
                return;
            }

            if (dateVal) {
                const selectedDate = new Date(dateVal);
                const today = new Date();
                today.setHours(23, 59, 59, 999);
                if (selectedDate > today) {
                    e.preventDefault();
                    alert('The date reported cannot be in the future.');
                    return;
                }
            }
        });
    }

    // -----------------------------------------------------------------------
    // Claim Submission Form Validation
    // -----------------------------------------------------------------------
    const claimForm = document.getElementById('claimForm');
    if (claimForm) {
        claimForm.addEventListener('submit', (e) => {
            const message = document.getElementById('claim-message')?.value?.trim();
            if (!message || message.length < 10) {
                e.preventDefault();
                alert('Please enter proof details of at least 10 characters to verify ownership.');
            }
        });
    }
});
