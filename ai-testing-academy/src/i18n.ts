/* Language selection + region injection.
   Picks the active language from ?lang= / localStorage / the browser, exposes it
   as L (content) and S (strings), and injects the four HTML regions + chrome. */
import type { Locale, StringKey } from './types.js';
import { $ } from './dom.js';
import { en } from './locales/en.js';
import { he } from './locales/he.js';

const CATALOG: Record<string, Locale> = { en, he };

function resolveLang(): string {
  const params = new URLSearchParams(location.search);
  let lang = params.get('lang')
    || localStorage.getItem('ata_lang')
    || ((navigator.language || 'en').toLowerCase().indexOf('he') === 0 ? 'he' : 'en');
  if (!CATALOG[lang]) lang = 'en';
  localStorage.setItem('ata_lang', lang);
  return lang;
}

export const activeLang: string = resolveLang();
export const L: Locale = CATALOG[activeLang];
export const S: Record<StringKey, string> = L.s;

/* Set <html> lang/dir and inject the nav/hero/main/footer fragments + chrome. */
export function applyLocale(): void {
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
