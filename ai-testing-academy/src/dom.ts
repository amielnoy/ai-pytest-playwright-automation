/* Tiny DOM helpers shared across the app. */

/* getElementById with a pragmatic widened type so call sites can read .value /
   .checked / .files / .options without per-call casts. Elements are assumed to
   exist (the shell defines them / i18n injects them before any handler runs). */
type AnyEl = HTMLInputElement & HTMLSelectElement & HTMLTextAreaElement;
export const $ = (id: string): AnyEl =>
  document.getElementById(id) as unknown as AnyEl;

const ESC_MAP: Record<string, string> =
  { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };

/* HTML-escape untrusted text (e.g. LLM output) before it touches innerHTML. */
export const esc = (s: unknown): string =>
  String(s == null ? '' : s).replace(/[&<>"']/g, c => ESC_MAP[c]);

/* True when the text contains Hebrew — used to flip generated resumes to RTL. */
export const isRtlText = (t: string): boolean => /[֐-׿]/.test(t);
