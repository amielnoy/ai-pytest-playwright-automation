/* Agent 1 — résumé evaluator: file upload (PDF/DOCX/TXT), scoring, and the
   honest job-tailored rewrite exported as a print-to-PDF. */
import type { EvalResult, EvalCategory } from './types.js';
import { $, esc, isRtlText } from './dom.js';
import { L, S } from './i18n.js';
import { callClaude, extractJSON } from './providers.js';

declare const pdfjsLib: any;
declare const mammoth: any;

/* ---------- lazy CDN loaders (PDF.js / Mammoth) ---------- */
function loadScript(src: string): Promise<string> {
  return new Promise((ok, bad) => {
    const existing = document.querySelector(`script[src="${src}"]`);
    if (existing) existing.remove();
    const s = document.createElement('script');
    s.src = src;
    s.onload = () => ok(src);
    s.onerror = () => { s.remove(); bad(new Error(src)); };
    document.head.appendChild(s);
  });
}

async function loadFirst(urls: string[], globalName: string): Promise<string | null> {
  if ((window as any)[globalName]) return null;
  const errors: string[] = [];
  for (const u of urls) {
    try { await loadScript(u); if ((window as any)[globalName]) return u; }
    catch (e) { errors.push((e as Error).message); }
  }
  throw new Error(S.errCdnFail + errors.join('\n'));
}

const PDFJS_V = '3.11.174', MAMMOTH_V = '1.8.0';
const PDFJS_URLS = [
  `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${PDFJS_V}/pdf.min.js`,
  `https://cdn.jsdelivr.net/npm/pdfjs-dist@${PDFJS_V}/build/pdf.min.js`,
  `https://unpkg.com/pdfjs-dist@${PDFJS_V}/build/pdf.min.js`
];
const MAMMOTH_URLS = [
  `https://cdnjs.cloudflare.com/ajax/libs/mammoth/${MAMMOTH_V}/mammoth.browser.min.js`,
  `https://cdn.jsdelivr.net/npm/mammoth@${MAMMOTH_V}/mammoth.browser.min.js`,
  `https://unpkg.com/mammoth@${MAMMOTH_V}/mammoth.browser.min.js`
];

async function extractPdf(file: File): Promise<string> {
  const loadedFrom = await loadFirst(PDFJS_URLS, 'pdfjsLib');
  if (loadedFrom) {
    pdfjsLib.GlobalWorkerOptions.workerSrc = loadedFrom.replace('pdf.min.js', 'pdf.worker.min.js');
  }
  const pdf = await pdfjsLib.getDocument({ data: await file.arrayBuffer() }).promise;
  const out: string[] = [];
  for (let i = 1; i <= pdf.numPages; i++) {
    const content = await (await pdf.getPage(i)).getTextContent();
    out.push(content.items.map((it: any) => it.str).join(' '));
  }
  return out.join('\n\n');
}

async function extractDocx(file: File): Promise<string> {
  await loadFirst(MAMMOTH_URLS, 'mammoth');
  const result = await mammoth.extractRawText({ arrayBuffer: await file.arrayBuffer() });
  return result.value;
}

export async function handleResumeFile(file: File | undefined): Promise<void> {
  if (!file) return;
  $('resumeErr').textContent = '';
  $('uploadLabel').textContent = S.uploadReading + file.name + '...';
  try {
    const ext = (file.name.split('.').pop() || '').toLowerCase();
    let text: string;
    if (ext === 'pdf') text = await extractPdf(file);
    else if (ext === 'docx') text = await extractDocx(file);
    else if (ext === 'txt') text = await file.text();
    else throw new Error(S.errFormatPrefix + ext + S.errFormatSuffix);
    text = text.replace(/[ \t]+/g, ' ').replace(/\n{3,}/g, '\n\n').trim();
    if (text.length < 40) throw new Error(S.errExtractFail);
    $('resumeText').value = text;
    $('uploadLabel').textContent = '✅ ' + file.name + S.uploadLoadedMid + text.length + S.uploadLoadedSuffix;
  } catch (e) {
    $('uploadLabel').textContent = S.uploadPrompt;
    $('resumeErr').textContent = (e as Error).message;
  }
}

/* ---------- evaluate ---------- */
const RESUME_SYSTEM = L.prompts.resume;
const IMPROVE_SYSTEM = L.prompts.improve;

interface LastEval { resume: string; role: string; evaluation: EvalResult; }
let lastEval: LastEval | null = null;
let improvedResume: string | null = null;

export async function evaluateResume(): Promise<void> {
  const txt = $('resumeText').value.trim();
  $('resumeErr').textContent = '';
  if (txt.length < 80) { $('resumeErr').textContent = S.errResumeEmpty; return; }
  const btn = $('resumeBtn');
  btn.disabled = true; btn.innerHTML = S.btnEvaluating;
  try {
    const role = $('targetRole').value.trim() || 'QA Automation Engineer';
    const reply = await callClaude(RESUME_SYSTEM,
      [{ role: 'user', content: S.promptRolePrefix + role + S.promptResumeLabel + txt }]);
    const r = extractJSON(reply) as EvalResult;
    $('resumeScore').textContent = String(r.overall);
    $('resumeScore').style.borderColor = r.overall >= 75 ? 'var(--green)' : r.overall >= 50 ? 'var(--yellow)' : 'var(--red)';
    $('resumeSummary').textContent = r.summary || '';
    $('resumeBars').innerHTML = (r.categories || []).map((c: EvalCategory) => {
      const pct = Math.max(0, Math.min(100, Number(c.score) || 0));
      return `<div class="bar-row" role="img" aria-label="${esc(c.name)}: ${pct} / 100"><div class="bar-label" aria-hidden="true"><span>${esc(c.name)}</span><span>${pct}</span></div>
       <div class="bar"><div style="width:${pct}%"></div></div></div>`;
    }).join('');
    const fill = (id: string, arr?: string[]) => $(id).innerHTML = (arr || []).map(x => `<li>${esc(x)}</li>`).join('');
    fill('resumeStrengths', r.strengths); fill('resumeGaps', r.gaps); fill('resumeRecs', r.recommendations);
    lastEval = { resume: txt, role, evaluation: r };
    improvedResume = null;
    $('improvedWrap').style.display = 'none';
    $('resumeResult').style.display = 'block';
  } catch (e) { $('resumeErr').textContent = (e as Error).message; }
  btn.disabled = false; btn.textContent = S.btnEvaluate;
}

/* ---------- improved résumé: generate / show / download as PDF ---------- */
async function ensureImprovedResume(): Promise<string> {
  if (improvedResume) return improvedResume;
  if (!lastEval) throw new Error(S.errNoEval);
  const jd = ($('jobDesc') ? $('jobDesc').value : '').trim();
  const reply = await callClaude(IMPROVE_SYSTEM, [{
    role: 'user',
    content: S.promptRolePrefixImprove + lastEval.role +
      (jd ? S.promptJobDescLabel + jd : '') +
      S.promptEvalResultsLabel + JSON.stringify({ gaps: lastEval.evaluation.gaps, recommendations: lastEval.evaluation.recommendations }) +
      S.promptOriginalResumeLabel + lastEval.resume
  }], 4000);
  improvedResume = reply.trim();
  return improvedResume;
}

export async function showImprovedResume(): Promise<void> {
  const btn = $('improveBtn');
  $('improvedErr').textContent = '';
  btn.disabled = true; btn.innerHTML = S.btnImproving;
  try {
    const text = await ensureImprovedResume();
    $('improvedText').textContent = text;
    $('improvedText').dir = isRtlText(text) ? 'rtl' : 'ltr';
    $('improvedWrap').style.display = 'block';
    $('improvedWrap').scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch (e) { $('improvedErr').textContent = (e as Error).message; }
  btn.disabled = false; btn.textContent = S.btnBuildResume;
}

export async function downloadImprovedPdf(): Promise<void> {
  const btn = $('pdfBtn');
  $('improvedErr').textContent = '';
  btn.disabled = true; btn.textContent = S.btnPreparingPdf;
  try {
    const text = await ensureImprovedResume();
    const rtl = isRtlText(text);
    const w = window.open('', '_blank');
    if (!w) throw new Error(S.errPopupBlocked);
    w.document.title = 'Resume — ' + lastEval!.role;
    w.document.documentElement.lang = rtl ? 'he' : 'en';
    w.document.documentElement.dir = rtl ? 'rtl' : 'ltr';
    const st = w.document.createElement('style');
    st.textContent = "body{font-family:'Segoe UI','Heebo',Arial,sans-serif;color:#222;max-width:800px;" +
      'margin:40px auto;padding:0 30px;line-height:1.55;font-size:13px;white-space:pre-wrap;}' +
      '@media print{body{margin:0 auto;}}';
    w.document.head.appendChild(st);
    w.document.body.textContent = text;
    w.focus();
    setTimeout(() => w.print(), 400);  // in the dialog choose "Save as PDF"
  } catch (e) { $('improvedErr').textContent = (e as Error).message; }
  btn.disabled = false; btn.textContent = S.btnDownloadPdf;
}

/* Wire the upload zone (click / drag-drop / keyboard), the job-desc invalidation,
   and kick off a background preload of the CDN libraries. */
export function initResume(): void {
  const zone = $('uploadZone');
  ['dragover', 'dragenter'].forEach(ev =>
    zone.addEventListener(ev, e => { e.preventDefault(); zone.classList.add('drag'); }));
  ['dragleave', 'drop'].forEach(ev =>
    zone.addEventListener(ev, e => { e.preventDefault(); zone.classList.remove('drag'); }));
  zone.addEventListener('drop', e => handleResumeFile((e as DragEvent).dataTransfer?.files[0]));
  zone.addEventListener('keydown', e => {
    const ev = e as KeyboardEvent;
    if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); $('resumeFile').click(); }
  });

  // Editing the job description invalidates a previously-built resume so it gets rebuilt for the new role.
  if ($('jobDesc')) $('jobDesc').addEventListener('input', () => { improvedResume = null; });

  window.addEventListener('load', () => {
    loadFirst(PDFJS_URLS, 'pdfjsLib').catch(() => {});
    loadFirst(MAMMOTH_URLS, 'mammoth').catch(() => {});
  });
}
