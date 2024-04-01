function toggleTheme() {
    let toggle_local = localStorage.mafiasi_theme == 'light' ? 'dark' : (localStorage.mafiasi_theme == 'dark' ? 'light' : 'media');
    let toggle_media = (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'light' : 'dark';
    let theme = (toggle_local == 'media') ? toggle_media : toggle_local;

    localStorage.mafiasi_theme = theme;

    document.documentElement.dataset.theme = theme
}

function disableSpecialFeature() {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0);
    document.cookie = `disable-special=True; path=/; expires=${tomorrow.toUTCString()}; Secure`;
    window.location.reload()
}

document.querySelector('#specialfeature-off').addEventListener('click', disableSpecialFeature)
