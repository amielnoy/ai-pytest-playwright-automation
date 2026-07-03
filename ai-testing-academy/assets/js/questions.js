/* A curated bank of real, commonly-asked QA-Automation interview questions,
   grouped by the same five stages the interview agent (Agent 2) runs. Rendered as
   a collapsible section so candidates can read the questions and then practice each
   stage live with the agent. Bilingual; built in JS so the big locale HTML fragments
   stay untouched. (A static client-only site can't scrape at runtime — CORS — and
   there's no reliable public interview-question API; see README for a build-time
   generator if you want this refreshed from public sources.) */
import { $ } from './dom.js';
import { esc } from './dom.js';
import { activeLang } from './i18n.js';
const EN = {
    nav: '❓ Interview Questions',
    title: '❓ Real Interview Questions',
    lead: 'The questions QA-Automation candidates actually get, grouped by the five interview stages. Read them, prepare your STAR answers, then run a live mock with the agent above.',
    note: '💡 Practice these out loud with Agent 2 — turn on 🔊 Voice for a hands-free mock interview.',
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
export function initQuestions() {
    const bank = activeLang === 'he' ? HE : EN;
    const section = document.createElement('section');
    section.id = 'interview-questions';
    section.innerHTML =
        `<h2>${esc(bank.title)}</h2><p class="lead">${esc(bank.lead)}</p>` +
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
}
