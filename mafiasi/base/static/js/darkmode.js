function applyTheme(theme) {
    document.querySelector('body').classList.remove('theme--dark');
    document.querySelector('body').classList.remove('theme--light');
    document.querySelector('body').classList.add(`theme--${theme}`);
}

function toggleTheme() {
    let mafiasi_theme = localStorage.getItem('mafiasi_theme');
    let toggle_local = mafiasi_theme == 'light' ? 'dark' : (mafiasi_theme == 'dark' ? 'light' : 'media');
    let toggle_media = (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'light' : 'dark';
    let theme = (toggle_local == 'media') ? toggle_media : toggle_local;

    localStorage.setItem('mafiasi_theme', theme);

    applyTheme(theme);
}

if (localStorage.getItem('mafiasi_theme')) applyTheme(localStorage.getItem('mafiasi_theme'));

document.querySelector('#theme-toggle').addEventListener('click', toggleTheme)
