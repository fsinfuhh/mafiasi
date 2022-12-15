function toggleTheme() {
    let toggle_local = localStorage.mafiasi_theme == 'light' ? 'dark' : (localStorage.mafiasi_theme == 'dark' ? 'light' : 'media');
    let toggle_media = (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'light' : 'dark';
    let theme = (toggle_local == 'media') ? toggle_media : toggle_local;

    localStorage.mafiasi_theme = theme;

    document.documentElement.dataset.theme = theme
}

document.querySelector('#theme-toggle').addEventListener('click', toggleTheme)
