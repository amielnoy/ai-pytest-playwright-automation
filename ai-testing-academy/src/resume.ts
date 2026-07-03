/* Agent 1 — résumé evaluator: file upload (PDF/DOCX/TXT), scoring, and the
   honest job-tailored rewrite exported as a print-to-PDF. */
import type { EvalResult, EvalCategory } from './types.js';
import { $, esc, isRtlText } from './dom.js';
import { L, S } from './i18n.js';
import { callClaude, extractJSON } from './providers.js';

declare const pdfjsLib: any;
declare const mammoth: any;
declare const html2canvas: any;

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
const JSPDF_V = '2.5.2', HTML2CANVAS_V = '1.4.1';
const JSPDF_URLS = [
  `https://cdnjs.cloudflare.com/ajax/libs/jspdf/${JSPDF_V}/jspdf.umd.min.js`,
  `https://cdn.jsdelivr.net/npm/jspdf@${JSPDF_V}/dist/jspdf.umd.min.js`,
  `https://unpkg.com/jspdf@${JSPDF_V}/dist/jspdf.umd.min.js`
];
const HTML2CANVAS_URLS = [
  `https://cdnjs.cloudflare.com/ajax/libs/html2canvas/${HTML2CANVAS_V}/html2canvas.min.js`,
  `https://cdn.jsdelivr.net/npm/html2canvas@${HTML2CANVAS_V}/dist/html2canvas.min.js`,
  `https://unpkg.com/html2canvas@${HTML2CANVAS_V}/dist/html2canvas.min.js`
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

/* A4 at 96dpi is 794px wide; render RTL to a canvas at that width so 1px ≈ 1:1. */
function fileName(role: string): string {
  return ('Resume - ' + role).replace(/[\\/:*?"<>|]+/g, '-').trim().slice(0, 80) + '.pdf';
}

/* English: real, selectable, ATS-parseable text via jsPDF's text API. */
function pdfFromText(text: string): any {
  const { jsPDF } = (window as any).jspdf;
  const pdf = new jsPDF('p', 'mm', 'a4');
  const margin = 15, lineH = 5;
  const pageW = pdf.internal.pageSize.getWidth();
  const pageH = pdf.internal.pageSize.getHeight();
  pdf.setFont('helvetica', 'normal'); pdf.setFontSize(10.5);
  const lines: string[] = pdf.splitTextToSize(text, pageW - margin * 2);
  let y = margin;
  for (const line of lines) {
    if (y + lineH > pageH - margin) { pdf.addPage(); y = margin; }
    pdf.text(line, margin, y);
    y += lineH;
  }
  return pdf;
}

/* Hebrew: jsPDF's built-in fonts have no Hebrew glyphs, so render the browser's
   own RTL layout to a canvas and paginate it into the PDF. */
async function pdfFromCanvas(text: string): Promise<any> {
  await loadFirst(HTML2CANVAS_URLS, 'html2canvas');
  const holder = document.createElement('div');
  holder.dir = 'rtl';
  holder.textContent = text;
  holder.style.cssText = 'position:fixed;left:-9999px;top:0;width:794px;background:#fff;color:#222;' +
    "padding:48px;font-family:'Segoe UI','Heebo',Arial,sans-serif;font-size:14px;line-height:1.6;" +
    'white-space:pre-wrap;word-wrap:break-word;';
  document.body.appendChild(holder);
  try {
    const canvas = await html2canvas(holder, { scale: 2, backgroundColor: '#ffffff' });
    const { jsPDF } = (window as any).jspdf;
    const pdf = new jsPDF('p', 'mm', 'a4');
    const pageW = pdf.internal.pageSize.getWidth();
    const pageH = pdf.internal.pageSize.getHeight();
    const imgH = canvas.height * pageW / canvas.width;
    const imgData = canvas.toDataURL('image/png');
    let heightLeft = imgH, position = 0;
    pdf.addImage(imgData, 'PNG', 0, position, pageW, imgH);
    heightLeft -= pageH;
    while (heightLeft > 0) {
      position -= pageH;
      pdf.addPage();
      pdf.addImage(imgData, 'PNG', 0, position, pageW, imgH);
      heightLeft -= pageH;
    }
    return pdf;
  } finally {
    holder.remove();
  }
}

export async function downloadImprovedPdf(): Promise<void> {
  const btn = $('pdfBtn');
  $('improvedErr').textContent = '';
  btn.disabled = true; btn.textContent = S.btnPreparingPdf;
  try {
    const text = await ensureImprovedResume();
    await loadFirst(JSPDF_URLS, 'jspdf');
    const pdf = isRtlText(text) ? await pdfFromCanvas(text) : pdfFromText(text);
    pdf.save(fileName(lastEval!.role));   // triggers a real file download
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
