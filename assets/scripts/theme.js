'use strict';

const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

const getPreferredTheme = () => {
    return localStorage.getItem('theme') || 'auto';
};

const getResolvedTheme = theme => {
    if (theme === 'auto') {
        return mediaQuery.matches ? 'dark' : 'light';
    }

    return theme;
};

const setTheme = theme => {
    document.documentElement.setAttribute(
        'data-bs-theme',
        getResolvedTheme(theme)
    );
};

const updateThemeUI = theme => {
    const themeIcon = document.querySelector('.theme-icon-active');
    const themeButtons = document.querySelectorAll('[data-bs-theme-value]');

    if (!themeIcon) {
        return;
    }

    const icons = {
        light: 'sun-fill.svg',
        dark: 'moon-stars-fill.svg',
        auto: 'circle-half.svg'
    };

    themeIcon.src = `assets/images/${icons[theme]}`;

    themeButtons.forEach(button => {
        const isActive = button.dataset.bsThemeValue === theme;

        button.classList.toggle('active', isActive);
        button.setAttribute('aria-pressed', isActive);

        const check = button.querySelector('.theme-check');

        if (check) {
            check.classList.toggle('d-none', !isActive);
        }
    });
};

const applyTheme = theme => {
    setTheme(theme);
    updateThemeUI(theme);
};

const initializeTheme = () => {
    const themeButtons = document.querySelectorAll('[data-bs-theme-value]');

    if (!themeButtons.length) {
        return;
    }

    const currentTheme = getPreferredTheme();

    applyTheme(currentTheme);

    themeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const theme = button.dataset.bsThemeValue;

            localStorage.setItem('theme', theme);
            applyTheme(theme);
        });
    });
};

// Apply the theme immediately.
// This doesn't require the navbar to exist.
setTheme(getPreferredTheme());

// Initialize once HTMX has loaded the navbar.
document.body.addEventListener('htmx:afterSwap', event => {
    if (event.detail.target.id === 'navbar') {
        initializeTheme();
    }
});
    
// Handle OS theme changes when using Auto.
mediaQuery.addEventListener('change', () => {
    if (getPreferredTheme() === 'auto') {
        setTheme('auto');
        updateThemeUI('auto');
    }
});