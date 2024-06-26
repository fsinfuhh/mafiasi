function toggleTheme() {
    let toggle_local = localStorage.mafiasi_theme == 'light' ? 'dark' : (localStorage.mafiasi_theme == 'dark' ? 'light' : 'media');
    let toggle_media = (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'light' : 'dark';
    let theme = (toggle_local == 'media') ? toggle_media : toggle_local;

    localStorage.mafiasi_theme = theme;

    document.documentElement.dataset.theme = theme
}

document.querySelector('#theme-toggle').addEventListener('click', toggleTheme)

function disableSpecialFeature() {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0);
    document.cookie = `disable-special=True; path=/; expires=${tomorrow.toUTCString()}; Secure`;
    let url = new URL(location.href);
    url.searchParams.delete('specialFeature');
    url.searchParams.delete('persistSpecialFeatureForThisSession');
    window.location.href = url
}

function enableSpecialFeature() {
    document.cookie = `disable-special=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; Secure`;
    window.location.reload()
}

const specialOff = document.querySelector('#special-off');
const specialOn = document.querySelector('#special-on');
if(specialOff) specialOff.addEventListener('click', disableSpecialFeature)
if(specialOn) specialOn.addEventListener('click', enableSpecialFeature)

if("feature" in document.querySelector('html').dataset){
    const feature = document.querySelector('html').dataset.feature
    const url = new URL(location.href);
    url.searchParams.set("specialFeature", feature);
    url.searchParams.set("persistSpecialFeatureForThisSession", "featurePersisted" in document.querySelector('html').dataset ? 'true' : 'undefined');
    history.pushState({}, "", url);
}
