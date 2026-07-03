/* A curated bank of real, commonly-asked QA-Automation interview questions,
   grouped by the same five stages the interview agent (Agent 2) runs — plus an
   optional "Enrich with AI" control that asks Gemini (the default provider) for the
   most-searched interview questions for a role, each with a concise model answer.
   Rendered as a collapsible section; built in JS so the big locale HTML fragments
   stay untouched. Bilingual. */
import { $, esc } from './dom.js';
import { activeLang } from './i18n.js';
import { callGeminiGrounded, extractJSON } from './providers.js';
/* Seed keywords always mixed into the grounded search, on top of the entered role. */
const SEED_KEYWORDS = 'AI dev, AI test automation, Playwright, pytest, Page Object Model, flaky tests, CI/CD, Docker, API testing, SDET, AI/LLM testing';
/* A real full interview to watch before practising. */
const INTERVIEW_VIDEO_ID = 'gl2TVA4JLpc';
const EN = {
    nav: '❓ Interview Questions',
    title: '❓ Real Interview Questions',
    lead: 'The questions QA-Automation candidates actually get, grouped by the five interview stages. Read them, prepare your STAR answers, then run a live mock with the agent above.',
    note: '💡 Practice these out loud with Agent 2 — turn on 🔊 Voice for a hands-free mock interview.',
    videoHeading: '🎥 Watch a real interview first',
    enrichCta: '✨ Enrich with AI',
    enrichPlaceholder: 'Role or keywords (e.g. SDET, Playwright, CI/CD)',
    enrichHint: 'Uses Gemini with live Google Search to pull the QA / AI-test-automation interview questions most searched in the last 3 months — each with a model answer. Needs a Gemini key in the Connection Setup above.',
    enriching: '✨ Enriching…',
    enrichHeading: '✨ AI-enriched Q&A — trending in the last 3 months',
    roleDefault: 'QA Automation Engineer',
    langName: 'English',
    stages: [
        { icon: '🧭', title: 'Stage 1 — HR & Motivation', items: [
                'Walk me through your background and why you moved into test automation.',
                'Why are you leaving your current role, and what are you looking for next?',
                'Tell me about a project you are proud of — what was your specific contribution?',
                'Describe a conflict with a developer over a bug. How did you resolve it?',
                'Where do you see QA automation heading in the next few years?'
            ] },
        { icon: '🎭', title: 'Stage 2 — Test Automation Knowledge', items: [
                'What is the Page Object Model and what problem does it solve?',
                'How do you decide what to automate and what to leave as manual testing?',
                'A test passes locally but is flaky in CI. How do you diagnose and fix it?',
                'Explicit vs. implicit waits — when do you use each, and why avoid fixed sleeps?',
                'How do you keep tests isolated and independent of execution order?',
                'How would you structure a suite across UI, API, and unit layers (the test pyramid)?'
            ] },
        { icon: '🧩', title: 'Stage 3 — Code & API', items: [
                'Explain pytest fixtures and fixture scope. When would you use a session fixture?',
                'How do you parametrize a test to run the same logic over many inputs?',
                'How do you test a REST API — status codes, schema, and negative cases?',
                'When do you mock a dependency versus hitting the real service?',
                'Write a function that reverses the words in a sentence. How would you test it?',
                'How do you make write operations (POST/PUT) safe to retry?'
            ] },
        { icon: '🐳', title: 'Stage 4 — DevOps & CI', items: [
                'Why run tests in Docker, and what makes a build reproducible?',
                'Walk me through a CI pipeline that runs your tests on every pull request.',
                'How do you speed up a slow suite — parallelism, sharding, test selection?',
                'How do you surface results: reports, trends, and failure screenshots?',
                'How do you handle secrets and environment config in CI?'
            ] },
        { icon: '🤖', title: 'Stage 5 — AI Testing', items: [
                'How do you test a feature powered by an LLM deterministically?',
                'What is prompt injection, and how would you write a test that proves it is blocked?',
                'How do you check that a model response does not leak secrets or PII (DLP)?',
                'How can AI agents help you write or triage tests — and where is human review required?',
                'How would you evaluate the quality of an AI feature beyond a simple pass/fail?'
            ] }
    ]
};
const HE = {
    nav: '❓ שאלות ראיון',
    title: '❓ שאלות ראיון אמיתיות',
    lead: 'השאלות שמועמדי QA Automation באמת נשאלים, מחולקות לחמשת שלבי הראיון. קראו, הכינו תשובות בשיטת STAR, ואז הריצו סימולציה חיה עם הסוכן למעלה.',
    note: '💡 תרגלו בקול רם עם סוכן 2 — הפעילו 🔊 קול לראיון סימולציה ללא ידיים.',
    videoHeading: '🎥 צפו בראיון אמיתי לפני שמתחילים',
    enrichCta: '✨ העשר עם AI',
    enrichPlaceholder: 'תפקיד או מילות מפתח (למשל SDET, Playwright, CI/CD)',
    enrichHint: 'משתמש ב-Gemini עם חיפוש Google חי כדי להביא את שאלות הראיון (QA ואוטומציית בדיקות מבוססת AI) המחופשות ביותר ב-3 החודשים האחרונים — כל אחת עם תשובת מודל. דורש מפתח Gemini באזור החיבור למעלה.',
    enriching: '✨ מעשיר…',
    enrichHeading: '✨ שו"ת בהעשרת AI — מגמות 3 החודשים האחרונים',
    roleDefault: 'מהנדס/ת אוטומציית QA',
    langName: 'Hebrew',
    stages: [
        { icon: '🧭', title: 'שלב 1 — משאבי אנוש ומוטיבציה', items: [
                'ספר על הרקע שלך ולמה עברת לאוטומציית בדיקות.',
                'למה אתה עוזב את התפקיד הנוכחי, ומה אתה מחפש בתפקיד הבא?',
                'ספר על פרויקט שאתה גאה בו — מה בדיוק הייתה התרומה שלך?',
                'תאר קונפליקט עם מפתח על באג. איך פתרת אותו?',
                'לאן לדעתך אוטומציית QA מתקדמת בשנים הקרובות?'
            ] },
        { icon: '🎭', title: 'שלב 2 — ידע באוטומציית בדיקות', items: [
                'מהו Page Object Model ואיזו בעיה הוא פותר?',
                'איך אתה מחליט מה לאוטמט ומה להשאיר כבדיקה ידנית?',
                'בדיקה עוברת מקומית אך מתנדנדת (flaky) ב-CI. איך תאבחן ותתקן?',
                'המתנות מפורשות מול משתמעות — מתי כל אחת, ולמה להימנע מ-sleep קבוע?',
                'איך אתה שומר על בדיקות מבודדות ובלתי תלויות בסדר ההרצה?',
                'איך היית בונה סוויטה על פני שכבות UI, API ו-unit (פירמידת הבדיקות)?'
            ] },
        { icon: '🧩', title: 'שלב 3 — קוד ו-API', items: [
                'הסבר fixtures ב-pytest ואת ה-scope שלהם. מתי תשתמש ב-session fixture?',
                'איך תפעיל parametrize כדי להריץ את אותה לוגיקה על קלטים רבים?',
                'איך אתה בודק REST API — קודי סטטוס, סכימה ומקרי קצה שליליים?',
                'מתי למקק (mock) תלות ומתי לפנות לשירות האמיתי?',
                'כתוב פונקציה שהופכת את סדר המילים במשפט. איך תבדוק אותה?',
                'איך אתה הופך פעולות כתיבה (POST/PUT) לבטוחות ל-retry?'
            ] },
        { icon: '🐳', title: 'שלב 4 — DevOps ו-CI', items: [
                'למה להריץ בדיקות ב-Docker, ומה הופך build לשחזורי?',
                'תאר pipeline של CI שמריץ את הבדיקות בכל pull request.',
                'איך תאיץ סוויטה איטית — מקביליות, sharding, בחירת בדיקות?',
                'איך אתה חושף תוצאות: דוחות, מגמות וצילומי מסך של כשלים?',
                'איך אתה מטפל בסודות ובקונפיגורציית סביבה ב-CI?'
            ] },
        { icon: '🤖', title: 'שלב 5 — בדיקות AI', items: [
                'איך אתה בודק פיצ\'ר שמבוסס LLM בצורה דטרמיניסטית?',
                'מהו prompt injection, ואיך תכתוב בדיקה שמוכיחה שהוא נחסם?',
                'איך אתה מוודא שתשובת המודל לא מדליפה סודות או מידע אישי (DLP)?',
                'איך סוכני AI יכולים לעזור לכתוב או למיין בדיקות — ואיפה נדרשת בקרת אדם?',
                'איך היית מעריך את איכות פיצ\'ר ה-AI מעבר ל-pass/fail פשוט?'
            ] }
    ]
};
const SYSTEM = 'You are a senior QA-Automation interviewer and career coach. Return ONLY valid JSON, no prose.';
/* Ask the AI for the most-searched interview questions (with model answers) for a role. */
async function enrich(bank) {
    const btn = $('qaEnrichBtn');
    const err = $('qaEnrichErr');
    const out = $('qaEnriched');
    err.textContent = '';
    const role = $('qaKeywords').value.trim() || bank.roleDefault;
    btn.disabled = true;
    btn.textContent = bank.enriching;
    try {
        const user = 'You have Google Search — use it. Find the QA / test-automation interview questions that have been ' +
            'most commonly asked and searched in the LAST 3 MONTHS, seeding the search with these keywords: ' +
            `${SEED_KEYWORDS}, ${role}. Prioritise current, trending topics — especially AI in development and ` +
            'test automation. Return the 8 highest-value questions a candidate should prepare now, each with a ' +
            'concise 2-4 sentence model answer. ' +
            'Return ONLY JSON: {"questions":[{"stage":"...","question":"...","answer":"...","keywords":["..."]}]}. ' +
            `Write every question and answer in ${bank.langName}.`;
        const reply = await callGeminiGrounded(SYSTEM, user, 3000);
        const items = (extractJSON(reply).questions || []);
        out.innerHTML =
            `<h3>${esc(bank.enrichHeading)} — ${esc(role)}</h3>` +
                items.map(q => `<details class="agent-box"><summary><h3 style="display:inline;margin:0;">${esc(q.question)}</h3></summary>` +
                    `<p style="margin-top:12px;">${esc(q.answer || '')}</p>` +
                    `<div>${(q.keywords || []).map(k => `<span class="tag">${esc(k)}</span>`).join(' ')}` +
                    (q.stage ? `<span class="notice" style="margin-inline-start:8px;">${esc(q.stage)}</span>` : '') +
                    '</div></details>').join('');
    }
    catch (e) {
        err.textContent = e.message;
    }
    btn.disabled = false;
    btn.textContent = bank.enrichCta;
}
export function initQuestions() {
    const bank = activeLang === 'he' ? HE : EN;
    const section = document.createElement('section');
    section.id = 'interview-questions';
    section.innerHTML =
        `<h2>${esc(bank.title)}</h2><p class="lead">${esc(bank.lead)}</p>` +
            // a real interview to watch first
            `<h3>${esc(bank.videoHeading)}</h3>` +
            `<div class="video-embed"><iframe src="https://www.youtube-nocookie.com/embed/${INTERVIEW_VIDEO_ID}" ` +
            `title="${esc(bank.videoHeading)}" loading="lazy" allowfullscreen ` +
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe></div>' +
            // AI enrichment control
            '<div class="agent-box">' +
            '<div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">' +
            `<input type="text" id="qaKeywords" placeholder="${esc(bank.enrichPlaceholder)}" style="flex:1; min-width:220px;">` +
            `<button type="button" class="primary" id="qaEnrichBtn" style="margin-top:0;">${esc(bank.enrichCta)}</button>` +
            '</div>' +
            `<p class="notice">${esc(bank.enrichHint)}</p>` +
            '<div id="qaEnrichErr" class="error" role="alert"></div>' +
            '<div id="qaEnriched" role="region" aria-live="polite"></div>' +
            '</div>' +
            // curated bank
            bank.stages.map(stage => `<details class="agent-box"><summary><h3 style="display:inline;margin:0;">${esc(stage.icon + ' ' + stage.title)}</h3></summary>` +
                `<ul style="margin-top:14px;">${stage.items.map(q => `<li>${esc(q)}</li>`).join('')}</ul></details>`).join('') +
            `<p class="notice">${esc(bank.note)}</p>`;
    const anchor = document.getElementById('interview-talk');
    if (anchor)
        anchor.after(section);
    else
        $('main-content').appendChild(section);
    const navAnchor = document.querySelector('nav a[href="#interview-talk"]');
    if (navAnchor) {
        const link = document.createElement('a');
        link.className = 'link';
        link.href = '#interview-questions';
        link.textContent = bank.nav;
        navAnchor.after(link);
    }
    $('qaEnrichBtn').addEventListener('click', () => enrich(bank));
    $('qaKeywords').addEventListener('keydown', e => {
        if (e.key === 'Enter') {
            e.preventDefault();
            enrich(bank);
        }
    });
}
