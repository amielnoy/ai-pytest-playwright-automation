/* Tiny DOM helpers shared across the app. */
export const $ = (id) => document.getElementById(id);
const ESC_MAP = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
/* HTML-escape untrusted text (e.g. LLM output) before it touches innerHTML. */
export const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, c => ESC_MAP[c]);
/* True when the text contains Hebrew — used to flip generated resumes to RTL. */
export const isRtlText = (t) => /[֐-׿]/.test(t);
