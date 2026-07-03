import { $ } from './dom.js';
import { en } from './locales/en.js';
import { he } from './locales/he.js';
const CATALOG = { en, he };
function resolveLang() {
    const params = new URLSearchParams(location.search);
    let lang = params.get('lang')
        || localStorage.getItem('ata_lang')
        || ((navigator.language || 'en').toLowerCase().indexOf('he') === 0 ? 'he' : 'en');
    if (!CATALOG[lang])
        lang = 'en';
    localStorage.setItem('ata_lang', lang);
    return lang;
}
export const activeLang = resolveLang();
export const L = CATALOG[activeLang];
export const S = L.s;
/* Set <html> lang/dir and inject the nav/hero/main/footer fragments + chrome. */
export function applyLocale() {
    const root = document.documentElement;
    root.lang = activeLang;
    root.dir = L.dir;
    $('nav').innerHTML = L.nav;
    $('hero').innerHTML = L.hero;
    $('main-content').innerHTML = L.main;
    $('site-footer').innerHTML = L.footer;
    if (L.ui) {
        $('skipLink').textContent = L.ui.skip;
        $('navToggle').setAttribute('aria-label', L.ui.navOpen);
        $('toTop').setAttribute('aria-label', L.ui.toTop);
    }
}
