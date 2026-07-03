/* AI Testing Academy — shared app. Locale (content + strings + prompts) comes from assets/i18n/<lang>.js */
var __ACADEMY = window.__ACADEMY || {};
var __params = new URLSearchParams(location.search);
var lang = __params.get('lang') || localStorage.getItem('ata_lang') || ((navigator.language||'en').toLowerCase().indexOf('he')===0 ? 'he' : 'en');
if (!__ACADEMY[lang]) lang = 'en';
localStorage.setItem('ata_lang', lang);
var L = __ACADEMY[lang];
var __S = L.s;
document.documentElement.lang = lang;
document.documentElement.dir = L.dir;
document.getElementById('nav').innerHTML = L.nav;
document.getElementById('hero').innerHTML = L.hero;
document.getElementById('main-content').innerHTML = L.main;
document.getElementById('site-footer').innerHTML = L.footer;
if (L.ui) {
  document.getElementById('skipLink').textContent = L.ui.skip;
  document.getElementById('navToggle').setAttribute('aria-label', L.ui.navOpen);
  document.getElementById('toTop').setAttribute('aria-label', L.ui.toTop);
}


/* ---------- shared API plumbing ---------- */
const $ = id => document.getElementById(id);

/* HTML-escape untrusted text (e.g. LLM output) before it touches innerHTML. */
const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g,
  c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const PROVIDERS = {
  gemini: {
    label: __S.keyLabelGemini,
    placeholder: "AIza...",
    models: ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"]
  },
  anthropic: {
    label: __S.keyLabelAnthropic,
    placeholder: "sk-ant-...",
    models: ["claude-sonnet-5", "claude-haiku-4-5-20251001"]
  },
  openai: {
    label: __S.keyLabelOpenai,
    placeholder: "sk-...",
    models: ["gpt-5-mini", "gpt-5.4-mini", "gpt-5.4"]
  }
};

function currentProvider() { return $("providerSel").value; }

/* keys loaded from .env (works when the page is served over http, e.g. python3 -m http.server) */
const envKeys = {};
const ENV_VAR_BY_PROVIDER = { gemini: "GEMINI_API_KEY", anthropic: "ANTHROPIC_API_KEY", openai: "OPENAI_API_KEY" };

async function loadEnvFile() {
  try {
    const res = await fetch("../.env", { cache: "no-store" });
    if (!res.ok) return;
    for (const line of (await res.text()).split("\n")) {
      const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.+?)\s*$/);
      if (m && !m[1].startsWith("#")) envKeys[m[1]] = m[2].replace(/^["']|["']$/g, "");
    }
    if (!ownKeyTouched) applyKeyMode();   // re-evaluate defaults; UI-saved keys still win
  } catch (_) { /* file:// or no .env — manual key entry still works */ }
}

function envKeyFor(provider) { return envKeys[ENV_VAR_BY_PROVIDER[provider]] || ""; }
let ownKeyTouched = false;   // becomes true once the user ticks the checkbox themselves

/* Gate the key input behind the checkbox: the .env key is the locked-in default,
   and a custom key can only be entered after ticking "Use my own API key". */
function applyKeyMode() {
  const p = PROVIDERS[currentProvider()];
  const envKey = envKeyFor(currentProvider());
  // default state (until the user touches the box): UI-saved key wins first,
  // then the .env key; own-key mode when there's no .env key at all.
  if (!ownKeyTouched)
    $("useOwnKey").checked = !!localStorage.getItem("ata_key_" + currentProvider()) || !envKey;
  const own = $("useOwnKey").checked;
  $("useOwnKey").disabled = !envKey;                 // can't turn off what doesn't exist
  $("ownKeyRow").style.opacity = envKey ? "1" : ".5";

  $("apiKey").disabled = !own;
  $("apiKey").placeholder = own ? p.placeholder : __S.placeholderEnvKey;
  if (own) {
    $("apiKey").value = localStorage.getItem("ata_key_" + currentProvider()) || "";
    $("apiKeyLabel").textContent = p.label;
  } else {
    $("apiKey").value = envKey;
    $("apiKeyLabel").textContent = p.label.replace(__S.labelSuffixLocal, __S.labelSuffixEnv);
  }
}

function onProviderChange() {
  const p = PROVIDERS[currentProvider()];
  $("modelSel").innerHTML = p.models.map(m => `<option value="${m}">${m}</option>`).join("");
  ownKeyTouched = false;   // each provider re-evaluates its own default
  applyKeyMode();
}
$("useOwnKey").addEventListener("change", () => { ownKeyTouched = true; applyKeyMode(); });
loadEnvFile();

$("providerSel").value = localStorage.getItem("ata_provider") || "gemini";
onProviderChange();
$("providerSel").addEventListener("change", () => localStorage.setItem("ata_provider", currentProvider()));
$("apiKey").addEventListener("change", () =>
  localStorage.setItem("ata_key_" + currentProvider(), $("apiKey").value.trim()));

async function callClaude(system, messages, maxTokens = 2500) {
  const key = $("apiKey").value.trim();
  if (!key) throw new Error(__S.errNoKey);
  if (currentProvider() === "anthropic" && !key.startsWith("sk-ant-"))
    throw new Error(__S.errKeyNotAnthropic);
  if (currentProvider() === "openai" && key.startsWith("sk-ant-"))
    throw new Error(__S.errKeyNotOpenai);
  const model = $("modelSel").value;
  let url, headers, body, parse;

  if (currentProvider() === "anthropic") {
    url = "https://api.anthropic.com/v1/messages";
    headers = {
      "content-type": "application/json",
      "x-api-key": key,
      "anthropic-version": "2023-06-01",
      "anthropic-dangerous-direct-browser-access": "true"
    };
    body = { model, max_tokens: maxTokens, system, messages };
    parse = d => d.content.filter(b => b.type === "text").map(b => b.text).join("\n");
  } else if (currentProvider() === "gemini") {
    url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent";
    headers = { "content-type": "application/json", "x-goog-api-key": key };
    body = {
      system_instruction: { parts: [{ text: system }] },
      contents: messages.map(m => ({
        role: m.role === "assistant" ? "model" : "user",
        parts: [{ text: m.content }]
      })),
      generationConfig: { maxOutputTokens: maxTokens }
    };
    if (model.includes("flash")) body.generationConfig.thinkingConfig = { thinkingBudget: 0 };
    parse = d => (d.candidates?.[0]?.content?.parts || []).map(p => p.text || "").join("\n");
  } else {
    url = "https://api.openai.com/v1/chat/completions";
    headers = {
      "content-type": "application/json",
      "Authorization": "Bearer " + key
    };
    body = {
      model,
      max_completion_tokens: maxTokens,
      messages: [{ role: "system", content: system }, ...messages]
    };
    parse = d => (d.choices?.[0]?.message?.content) || "";
  }

  let res;
  try {
    res = await fetch(url, { method: "POST", headers, body: JSON.stringify(body) });
  } catch (e) {
    throw new Error(
      __S.errBlockedPrefix + new URL(url).host + __S.errBlockedMid +
      __S.errBlockedCauses +
      __S.errBlockedTry +
      __S.errBlockedOpenUrl);
  }
  if (!res.ok) {
    const errBody = await res.text();
    let hint = "";
    if (currentProvider() === "gemini" && [400, 401, 403].includes(res.status) && !key.startsWith("AIza"))
      hint = __S.errGeminiKeyHint;
    throw new Error(__S.errApiPrefix + res.status + "): " + errBody.slice(0, 300) + hint);
  }
  return parse(await res.json());
}

function resetSettings() {
  Object.keys(localStorage).filter(k => k.startsWith("ata_")).forEach(k => localStorage.removeItem(k));
  location.reload();
}

async function testConnection() {
  const el = $("connStatus");
  el.style.color = "var(--muted)"; el.textContent = __S.statusTesting;
  try {
    const reply = await callClaude(__S.pingSystem, [{ role: "user", content: __S.pingUser }], 20);
    el.style.color = "var(--green)"; el.textContent = __S.statusOkPrefix + $("modelSel").value + "): " + reply.slice(0, 40);
  } catch (e) {
    el.style.color = "var(--red)"; el.textContent = "❌ " + e.message;
  }
}

function extractJSON(text) {
  const fenced = text.match(/```(?:json)?\s*([\s\S]*?)```/);
  const raw = fenced ? fenced[1] : text;
  const start = raw.indexOf("{"), end = raw.lastIndexOf("}");
  if (start === -1 || end === -1) throw new Error(__S.errNoJson);
  return JSON.parse(raw.slice(start, end + 1));
}

/* ---------- Resume file upload (PDF / DOCX / TXT) ---------- */
function loadScript(src) {
  return new Promise((ok, bad) => {
    const existing = document.querySelector(`script[src="${src}"]`);
    if (existing) { existing.remove(); }
    const s = document.createElement("script");
    s.src = src; s.onload = () => ok(src); s.onerror = () => { s.remove(); bad(new Error(src)); };
    document.head.appendChild(s);
  });
}

async function loadFirst(urls, globalName) {
  if (window[globalName]) return null;
  const errors = [];
  for (const u of urls) {
    try { await loadScript(u); if (window[globalName]) return u; }
    catch (e) { errors.push(e.message); }
  }
  throw new Error(__S.errCdnFail + errors.join("\n"));
}

const PDFJS_V = "3.11.174", MAMMOTH_V = "1.8.0";
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

async function extractPdf(file) {
  const loadedFrom = await loadFirst(PDFJS_URLS, "pdfjsLib");
  if (loadedFrom) {
    pdfjsLib.GlobalWorkerOptions.workerSrc = loadedFrom.replace("pdf.min.js", "pdf.worker.min.js");
  }
  const pdf = await pdfjsLib.getDocument({ data: await file.arrayBuffer() }).promise;
  let out = [];
  for (let i = 1; i <= pdf.numPages; i++) {
    const content = await (await pdf.getPage(i)).getTextContent();
    out.push(content.items.map(it => it.str).join(" "));
  }
  return out.join("\n\n");
}

async function extractDocx(file) {
  await loadFirst(MAMMOTH_URLS, "mammoth");
  const result = await mammoth.extractRawText({ arrayBuffer: await file.arrayBuffer() });
  return result.value;
}

window.addEventListener("load", () => {
  loadFirst(PDFJS_URLS, "pdfjsLib").catch(() => {});
  loadFirst(MAMMOTH_URLS, "mammoth").catch(() => {});
});

async function handleResumeFile(file) {
  if (!file) return;
  $("resumeErr").textContent = "";
  $("uploadLabel").textContent = __S.uploadReading + file.name + "...";
  try {
    const ext = file.name.split(".").pop().toLowerCase();
    let text;
    if (ext === "pdf") text = await extractPdf(file);
    else if (ext === "docx") text = await extractDocx(file);
    else if (ext === "txt") text = await file.text();
    else throw new Error(__S.errFormatPrefix + ext + __S.errFormatSuffix);
    text = text.replace(/[ \t]+/g, " ").replace(/\n{3,}/g, "\n\n").trim();
    if (text.length < 40) throw new Error(__S.errExtractFail);
    $("resumeText").value = text;
    $("uploadLabel").textContent = "✅ " + file.name + __S.uploadLoadedMid + text.length + __S.uploadLoadedSuffix;
  } catch (e) {
    $("uploadLabel").textContent = __S.uploadPrompt;
    $("resumeErr").textContent = e.message;
  }
}

const zone = $("uploadZone");
["dragover", "dragenter"].forEach(ev => zone.addEventListener(ev, e => { e.preventDefault(); zone.classList.add("drag"); }));
["dragleave", "drop"].forEach(ev => zone.addEventListener(ev, e => { e.preventDefault(); zone.classList.remove("drag"); }));
zone.addEventListener("drop", e => handleResumeFile(e.dataTransfer.files[0]));
zone.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); $("resumeFile").click(); } });

/* ---------- Agent 1: Resume evaluator ---------- */
const RESUME_SYSTEM = L.prompts.resume;

let lastEval = null;
let improvedResume = null;

async function evaluateResume() {
  const txt = $("resumeText").value.trim();
  $("resumeErr").textContent = "";
  if (txt.length < 80) { $("resumeErr").textContent = __S.errResumeEmpty; return; }
  const btn = $("resumeBtn");
  btn.disabled = true; btn.innerHTML = __S.btnEvaluating;
  try {
    const role = $("targetRole").value.trim() || "QA Automation Engineer";
    const reply = await callClaude(RESUME_SYSTEM,
      [{ role: "user", content: __S.promptRolePrefix + role + __S.promptResumeLabel + txt }]);
    const r = extractJSON(reply);
    $("resumeScore").textContent = r.overall;
    $("resumeScore").style.borderColor = r.overall >= 75 ? "var(--green)" : r.overall >= 50 ? "var(--yellow)" : "var(--red)";
    $("resumeSummary").textContent = r.summary || "";
    $("resumeBars").innerHTML = (r.categories || []).map(c => {
      const pct = Math.max(0, Math.min(100, Number(c.score) || 0));
      return `<div class="bar-row" role="img" aria-label="${esc(c.name)}: ${pct} / 100"><div class="bar-label" aria-hidden="true"><span>${esc(c.name)}</span><span>${pct}</span></div>
       <div class="bar"><div style="width:${pct}%"></div></div></div>`;
    }).join("");
    const fill = (id, arr) => $(id).innerHTML = (arr || []).map(x => `<li>${esc(x)}</li>`).join("");
    fill("resumeStrengths", r.strengths); fill("resumeGaps", r.gaps); fill("resumeRecs", r.recommendations);
    lastEval = { resume: txt, role, evaluation: r };
    improvedResume = null;
    $("improvedWrap").style.display = "none";
    $("resumeResult").style.display = "block";
  } catch (e) { $("resumeErr").textContent = e.message; }
  btn.disabled = false; btn.textContent = __S.btnEvaluate;
}

/* ---------- Improved resume: generate / show / download as PDF ---------- */
const IMPROVE_SYSTEM = L.prompts.improve;

async function ensureImprovedResume() {
  if (improvedResume) return improvedResume;
  if (!lastEval) throw new Error(__S.errNoEval);
  const jd = ($("jobDesc") ? $("jobDesc").value : "").trim();
  const reply = await callClaude(IMPROVE_SYSTEM, [{
    role: "user",
    content: __S.promptRolePrefixImprove + lastEval.role +
      (jd ? __S.promptJobDescLabel + jd : "") +
      __S.promptEvalResultsLabel + JSON.stringify({ gaps: lastEval.evaluation.gaps, recommendations: lastEval.evaluation.recommendations }) +
      __S.promptOriginalResumeLabel + lastEval.resume
  }], 4000);
  improvedResume = reply.trim();
  return improvedResume;
}

// Editing the job description invalidates a previously-built resume so it gets rebuilt for the new role.
if ($("jobDesc")) $("jobDesc").addEventListener("input", () => { improvedResume = null; });

async function showImprovedResume() {
  const btn = $("improveBtn");
  $("improvedErr").textContent = "";
  btn.disabled = true; btn.innerHTML = __S.btnImproving;
  try {
    const text = await ensureImprovedResume();
    $("improvedText").textContent = text;
    $("improvedText").dir = /[֐-׿]/.test(text) ? "rtl" : "ltr";
    $("improvedWrap").style.display = "block";
    $("improvedWrap").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (e) { $("improvedErr").textContent = e.message; }
  btn.disabled = false; btn.textContent = __S.btnBuildResume;
}

async function downloadImprovedPdf() {
  const btn = $("pdfBtn");
  $("improvedErr").textContent = "";
  btn.disabled = true; btn.textContent = __S.btnPreparingPdf;
  try {
    const text = await ensureImprovedResume();
    const rtl = /[֐-׿]/.test(text);
    const w = window.open("", "_blank");
    if (!w) throw new Error(__S.errPopupBlocked);
    w.document.title = "Resume — " + lastEval.role;
    w.document.documentElement.lang = rtl ? "he" : "en";
    w.document.documentElement.dir = rtl ? "rtl" : "ltr";
    const st = w.document.createElement("style");
    st.textContent = "body{font-family:'Segoe UI','Heebo',Arial,sans-serif;color:#222;max-width:800px;" +
      "margin:40px auto;padding:0 30px;line-height:1.55;font-size:13px;white-space:pre-wrap;}" +
      "@media print{body{margin:0 auto;}}";
    w.document.head.appendChild(st);
    w.document.body.textContent = text;
    w.focus();
    setTimeout(() => w.print(), 400);  // in the dialog choose "Save as PDF"
  } catch (e) { $("improvedErr").textContent = e.message; }
  btn.disabled = false; btn.textContent = __S.btnDownloadPdf;
}

/* ---------- Agent 2: Interview readiness ---------- */
const INTERVIEW_SYSTEM = L.prompts.interview;

let chat = [];
let interviewOn = false;

function addMsg(cls, text) {
  const div = document.createElement("div");
  div.className = "msg " + cls;
  div.textContent = text;
  $("chatBox").appendChild(div);
  $("chatBox").scrollTop = $("chatBox").scrollHeight;
  return div;
}

async function agentTurn() {
  const thinking = addMsg("sys", __S.statusInterviewerThinking);
  try {
    const reply = await callClaude(INTERVIEW_SYSTEM, chat, 1500);
    thinking.remove();
    chat.push({ role: "assistant", content: reply });
    addMsg("ai", reply);
  } catch (e) {
    thinking.remove();
    $("chatErr").textContent = e.message;
  }
}

async function startInterview() {
  $("chatErr").textContent = "";
  if (!$("apiKey").value.trim()) { $("chatErr").textContent = __S.errNoKeyInterview; return; }
  $("chatBox").innerHTML = "";
  chat = [{ role: "user", content: __S.interviewOpener }];
  interviewOn = true;
  $("chatInput").disabled = false; $("sendBtn").disabled = false; $("verdictBtn").disabled = false;
  $("startBtn").textContent = __S.btnRestartInterview;
  addMsg("user", __S.interviewOpenerMsg);
  await agentTurn();
}

async function sendAnswer() {
  if (!interviewOn) return;
  const val = $("chatInput").value.trim();
  if (!val) return;
  $("chatInput").value = "";
  $("chatErr").textContent = "";
  chat.push({ role: "user", content: val });
  addMsg("user", val);
  $("sendBtn").disabled = true;
  await agentTurn();
  $("sendBtn").disabled = false;
}

async function requestVerdict() {
  if (!interviewOn) return;
  $("chatErr").textContent = "";
  chat.push({ role: "user", content: "___VERDICT___" });
  addMsg("sys", __S.statusGeneratingVerdict);
  $("sendBtn").disabled = true; $("verdictBtn").disabled = true;
  await agentTurn();
  $("verdictBtn").disabled = false; $("sendBtn").disabled = false;
}

$("chatInput").addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendAnswer(); }
});

/* ---------- explainer videos: attach players, show placeholder if the file is missing ---------- */
document.querySelectorAll(".video-card").forEach(card => {
  const src = card.dataset.src;
  const v = document.createElement("video");
  v.controls = true; v.preload = "metadata"; v.src = src;
  v.setAttribute("aria-label", card.querySelector("h4").textContent);
  v.addEventListener("loadedmetadata", () => { ph.remove(); });
  v.addEventListener("error", () => {
    v.remove();
    ph.textContent = __S.videoMissingPrefix + src + __S.videoMissingSuffix;
  });
  const ph = document.createElement("div");
  ph.className = "no-video"; ph.textContent = __S.videoLoading;
  card.appendChild(v); card.appendChild(ph);
});

/* ---------- sidebar scroll-spy: highlight the section in view ---------- */
(() => {
  const links = [...document.querySelectorAll("nav a.link")].filter(a => a.getAttribute("href").startsWith("#"));
  const byId = Object.fromEntries(links.map(a => [a.getAttribute("href").slice(1), a]));
  const obs = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (en.isIntersecting) {
        links.forEach(a => a.classList.remove("active"));
        byId[en.target.id]?.classList.add("active");
      }
    });
  }, { rootMargin: "-25% 0px -65% 0px" });
  Object.keys(byId).forEach(id => { const s = document.getElementById(id); if (s) obs.observe(s); });
})();

/* ---------- scroll-reveal: sections & cards float in ---------- */
(() => {
  const targets = document.querySelectorAll("section > h2, section > .lead, section .card, section .agent-box, section pre, section table, section h3, section ul, section p");
  const io = new IntersectionObserver(es => es.forEach(en => {
    if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
  }), { rootMargin: "0px 0px -8% 0px" });
  targets.forEach(el => { el.classList.add("reveal"); io.observe(el); });
})();


/* ---------- UI/UX enhancement layer ---------- */
(function(){
  const $ = id => document.getElementById(id);
  const root = document.documentElement;

  /* theme — saved choice, else OS preference */
  const saved = localStorage.getItem("ata_theme");
  applyTheme(saved || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
  function applyTheme(t){
    root.setAttribute("data-theme", t);
    const dark = t === "dark";
    if ($("themeIcon")) $("themeIcon").textContent = dark ? "☀️" : "🌙";
    if ($("themeLabel")) $("themeLabel").textContent = dark ? __S.themeLabelLight : __S.themeLabelDark;
  }
  $("themeToggle") && $("themeToggle").addEventListener("click", () => {
    const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    localStorage.setItem("ata_theme", next); applyTheme(next);
  });

  /* scroll progress + back-to-top */
  const bar = $("scrollProgress"), toTop = $("toTop");
  function onScroll(){
    const h = root, max = h.scrollHeight - h.clientHeight;
    if (bar) bar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + "%";
    if (toTop) toTop.classList.toggle("show", h.scrollTop > 500);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  toTop && toTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

  /* mobile nav drawer */
  const navToggle = $("navToggle"), scrim = $("navScrim");
  const setNav = open => { document.body.classList.toggle("nav-open", open);
    navToggle && navToggle.setAttribute("aria-expanded", String(open)); };
  navToggle && navToggle.addEventListener("click", () => setNav(!document.body.classList.contains("nav-open")));
  scrim && scrim.addEventListener("click", () => setNav(false));
  document.querySelectorAll("nav a[href^='#']").forEach(a => a.addEventListener("click", () => setNav(false)));

  /* section-number chips in the nav */
  document.querySelectorAll("nav a.link[href^='#']").forEach(a => {
    const sec = document.querySelector(a.getAttribute("href"));
    const num = sec && sec.querySelector(".num") && sec.querySelector(".num").textContent.trim();
    if (num) { const s = document.createElement("span"); s.className = "nav-num";
      s.setAttribute("aria-hidden", "true"); s.textContent = num; a.prepend(s); }
  });

  /* copy-to-clipboard on code blocks */
  document.querySelectorAll("main pre").forEach(pre => {
    const wrap = document.createElement("div"); wrap.className = "pre-wrap";
    pre.parentNode.insertBefore(wrap, pre); wrap.appendChild(pre);
    const btn = document.createElement("button"); btn.type = "button";
    btn.className = "copy-btn"; btn.textContent = __S.copyBtn;
    btn.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(pre.innerText);
        btn.textContent = __S.copyBtnDone; btn.classList.add("copied");
        setTimeout(() => { btn.textContent = __S.copyBtnReset; btn.classList.remove("copied"); }, 1600);
      } catch (_) { btn.textContent = __S.copyBtnFail; }
    });
    wrap.appendChild(btn);
  });
})();
