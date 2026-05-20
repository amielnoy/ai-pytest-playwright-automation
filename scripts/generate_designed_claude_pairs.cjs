const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "..");
const SOURCE_DIR = process.env.CLAUDE_COWORK_INPUTS
  ? path.resolve(process.env.CLAUDE_COWORK_INPUTS)
  : path.join(ROOT, "claude_cowork_inputs");
const OUT_DIR = process.env.CLAUDE_COWORK_DESIGNED
  ? path.resolve(process.env.CLAUDE_COWORK_DESIGNED)
  : path.join(ROOT, "claude_cowork_designed");

function loadCommonJsData(filePath) {
  const code = fs.readFileSync(filePath, "utf8");
  const sandbox = { module: { exports: {} }, exports: {}, require, console };
  vm.runInNewContext(code, sandbox, { filename: filePath });
  return sandbox.module.exports;
}

const pairs = loadCommonJsData(path.join(SOURCE_DIR, "content_pairs.js"));

const palettes = [
  ["#0f4c5c", "#e36414", "#f7f2ea"],
  ["#243b53", "#2f9e44", "#eef6f0"],
  ["#253858", "#00a3bf", "#edf7fa"],
  ["#3c1642", "#d95d39", "#fbf0ec"],
  ["#284b63", "#9a8c98", "#f2f4f6"],
  ["#1b4332", "#b08968", "#f5efe7"],
  ["#3d405b", "#e07a5f", "#f7ede2"],
  ["#1f2937", "#7c3aed", "#f4f1ff"],
  ["#2b2d42", "#ef476f", "#fff0f3"],
  ["#0b3954", "#087e8b", "#edf9fb"],
];

const expansions = {
  1: {
    lecture:
      "המפגש הראשון מייצר שפה משותפת לקורס כולו. הוא מציב את ה-AI לא כגימיק נקודתי, אלא כשכבת עבודה שמשפיעה על איסוף מודיעין, כתיבת זיהויים, ניתוח אירועים וגם על דרך הפעולה של תוקפים. הדגש הוא להבין את המערכת השלמה: מודלים, נתונים, כלים, סיכונים ומדדים.",
    exercise:
      "בתרגול נבנה בסיס עבודה שממנו ימשיכו כל המעבדות הבאות. הסטודנטים מתקינים סביבה מבודדת, מריצים מודל מקומי ומתרגלים שימוש ראשוני ב-LLM ככלי עזר מבוקר. בסוף התרגול חשוב שכל משתתף יחזיק סביבת עבודה יציבה, מתועדת וניתנת לשחזור.",
  },
  2: {
    lecture:
      "כאן עוברים מתפיסה כללית של AI לשאלה מדידה: איך מזהים חריגה. המפגש מפריד בין אלגוריתמים קלאסיים, מודלים עמוקים ומדדי הערכה, ומראה מדוע Accuracy כמעט אף פעם לא מספיק בעולם סייבר לא מאוזן. המטרה היא לחשוב כמו Detection Engineer שמחבר מודל למציאות מבצעית.",
    exercise:
      "התרגול מתמקד בבניית ניסוי השוואתי. הסטודנטים מאמנים כמה גישות על אותו מידע, בוחנים טעויות, ומבינים איך החלטת סף אחת יכולה לשנות עומס SOC שלם. הדגש הוא לא רק להפיק גרף יפה, אלא להבין האם המודל מתאים להפעלה בארגון.",
  },
  3: {
    lecture:
      "המפגש מציב את שכבת הרשת כקו הגנה מרכזי. במקום להסתפק בחוקי חתימה, הוא מחבר לוגים של Zeek ו-Suricata לפיצ'רים שאפשר למדל, ומדגים כיצד תעבורה מוצפנת עדיין משאירה סימנים התנהגותיים. כך נבנית תפיסה שמשלבת Signature, Anomaly ו-ML.",
    exercise:
      "במעבדה הסטודנטים מחברים בין חיישני רשת, דאטהסט ומודל. התרגול מכוון להבנה מעשית של זרימת מידע: מאיסוף האירוע, דרך הפקת פיצ'רים, ועד החלטת זיהוי. בסיום יש בסיס ל-NIDS היברידי שניתן למדוד ולשפר.",
  },
  4: {
    lecture:
      "המפגש עוסק במתח שבין סיווג נוזקות לבין התחמקות. הוא משווה בין ניתוח סטטי, ניתוח דינמי ולמידה על קבצים בינאריים, ומחדד מדוע מודל טוב חייב להיבחן מול טכניקות Evasion. זוהי נקודת מפגש בין Data Science לבין Reverse Engineering.",
    exercise:
      "התרגול בונה Pipeline שמתחיל בחילוץ פיצ'רים ומסתיים במדידת עמידות. הסטודנטים מפעילים כלים הגנתיים והתקפיים באותו תרחיש כדי לראות איך שינוי קטן ב-Payload משנה את תוצאת הזיהוי. התוצר הוא מודל עם דוח חולשות ולא רק ציון ביצועים.",
  },
  5: {
    lecture:
      "במפגש זה המוקד עובר מזהות והתנהגות משתמש. UEBA דורש להבין רצפים, הקשר ארגוני, הרשאות וגרפים, ולכן הוא שונה מזיהוי אירוע בודד. המפגש מחבר בין Active Directory, לוגים, תנועה רוחבית וזיהוי דליפת מידע.",
    exercise:
      "המעבדה מתרגלת בניית תמונת התנהגות ולא רק איתור Alert. הסטודנטים יוצרים Baseline, מחפשים חריגה ברצפי התחברות ומנתחים קשרים בגרף. בסיום ניתן להסביר לא רק מה חריג, אלא למה הוא חשוד בהקשר הארגוני.",
  },
  6: {
    lecture:
      "המפגש מציג NLP ככלי לעיבוד מודיעין סייבר ולזיהוי מידע רגיש. הוא מחבר בין חילוץ IOC, בניית STIX, RAG מקומי ו-DLP מבוסס הקשר. המטרה היא להפוך טקסט חופשי למידע שניתן לחיפוש, תיוג ואכיפה.",
    exercise:
      "התרגול בונה שרשרת CTI מלאה: מקור טקסטואלי נכנס, מודלים מחלצים ישויות, המידע נשלח למערכות מודיעין, ומנגנון DLP בודק דליפות. הדגש הוא על איכות הנתונים ועל בקרות שמונעות מה-AI לחשוף מידע שלא אמור לצאת.",
  },
  7: {
    lecture:
      "המפגש מתמקד בפישינג כבעיה רב-שכבתית: URL, שפה, מותג, דומיין והתנהגות משתמש. הוא מראה מדוע אין סימן אחד שמספיק לזיהוי, וכיצד משלבים Feature Engineering עם NLP ומודלים חזותיים. זהו תרגול חשיבה על סיכון עסקי, לא רק סיווג הודעה.",
    exercise:
      "במעבדה הסטודנטים בונים מסנן שמחבר כמה מקורות ראיות. הם מנתחים URL, גוף הודעה וסימני התחזות, ואז בודקים את ההגנה מול דוגמאות Red Team. התוצר הרצוי הוא Pipeline שמסביר את ההחלטה ולא רק מחזיר True/False.",
  },
  8: {
    lecture:
      "המפגש מחבר AI לתהליכי SOC ו-DevSecOps. הוא מדגיש ש-AI לא מחליף תהליך, אלא חייב לשבת בתוך Pipeline עם הרשאות, Audit, Webhooks וגבולות פעולה. כאן מתחילים לחשוב על Agents כמערכות Production שדורשות בקרה.",
    exercise:
      "התרגול בונה אוטומציה מבוקרת סביב אירועים וקוד. הסטודנטים מחברים סריקות, Webhooks, סיכומי LLM ופתיחת Case, תוך הפרדה בין פעולה מותרת לפעולה שדורשת אישור אדם. התוצאה היא Flow שניתן לתפעל בסביבה אמיתית בזהירות.",
  },
  9: {
    lecture:
      "המפגש מציג את הצד המסוכן של מערכות AI: Prompt Injection, Jailbreaks, Supply Chain ו-MCP Security. הדגש הוא שמודל אינו גבול אבטחה, ולכן צריך לעצב מעטפת שמגבילה כלים, נתונים והרשאות. זהו מפגש קריטי לכל מי שבונה Agents.",
    exercise:
      "במעבדה הסטודנטים תוקפים ומקשיחים את אותה מערכת. הם מריצים ניסיונות Jailbreak, בוחנים Guardrails, ומוודאים שכלי MCP מוגבלים להקשר הנכון. התרגול מחייב מדידה: שיעור עקיפה, סוגי כשל, ומה השתפר אחרי הקשחה.",
  },
  10: {
    lecture:
      "המפגש המסכם מאחד את כל שכבות הקורס למערכת אחת: איסוף נתונים, מודלים, LLM Analyst, SOAR, DLP, DevSecOps ומדדים. הדגש הוא על ארכיטקטורה שניתן להגן עליה, להסביר אותה ולמדוד אותה. זו נקודת המעבר מתרגילים נפרדים לפרויקט הנדסי שלם.",
    exercise:
      "התרגול הוא פרויקט מסכם. הסטודנטים מתכננים, בונים, מגנים ומציגים מערכת Agentic AI Threat Detection מקצה לקצה. הצלחה נמדדת לא רק בקוד שעובד, אלא ביכולת להראות Threat Model, Pipeline, תוצאות Red Team ו-KPIs ברורים.",
  },
};

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function richText(value) {
  const text = String(value ?? "");
  const termPattern = /(\([A-Za-z0-9][A-Za-z0-9+./:_@#%& \-]*\)[,.]?|[A-Za-z0-9][A-Za-z0-9+./:_@#%& \-]*[A-Za-z0-9][,.]?)/g;
  let output = "";
  let lastIndex = 0;
  for (const match of text.matchAll(termPattern)) {
    output += escapeHtml(text.slice(lastIndex, match.index));
    output += `<span dir="ltr" class="term">${escapeHtml(match[0])}</span>`;
    lastIndex = match.index + match[0].length;
  }
  output += escapeHtml(text.slice(lastIndex));
  return output;
}

function slug(num, kind) {
  return `meeting_${String(num).padStart(2, "0")}_${kind}.html`;
}

function list(items, className = "") {
  if (!items || items.length === 0) return "";
  return `<ul class="${className}">${items.map((item) => `<li>${richText(item)}</li>`).join("")}</ul>`;
}

function labeledList(items, title) {
  if (!items || items.length === 0) return "";
  return `<section class="block">
    <h2>${richText(title)}</h2>
    ${list(items)}
  </section>`;
}

function prose(text, className = "") {
  if (!text) return "";
  const sentences = String(text)
    .split(/(?<=[.!?])\s+/)
    .map((part) => part.trim())
    .filter(Boolean);
  const groups = [];
  for (let index = 0; index < sentences.length; index += 2) {
    groups.push(sentences.slice(index, index + 2).join(" "));
  }
  return groups.map((part) => `<p class="${className}">${richText(part)}</p>`).join("");
}

function noteBox(title, text) {
  return `<section class="note-box">
    <h2>${richText(title)}</h2>
    ${prose(text)}
  </section>`;
}

function studyPath(pair) {
  const first = pair.lecture.sections[0]?.h || "פתיחה";
  const last = pair.lecture.sections[pair.lecture.sections.length - 1]?.h || "סיכום";
  return noteBox(
    "איך ללמוד את המפגש",
    `התחילו מהרעיון המרכזי של ${first}, ואז עברו בהדרגה אל ${last}. במהלך הקריאה כדאי לסמן מושגים שחוזרים בכמה סעיפים, משום שהם יהפכו לצעדים מעשיים בתרגול. בסוף ההרצאה ודאו שאתם יכולים להסביר את הקשר בין הכלים, הנתונים והמדדים בלי להסתמך על רשימת פקודות בלבד.`,
  );
}

function exercisePath(pair) {
  const taskNames = pair.exercise.tasks.slice(0, 3).map((task) => task.name).join(", ");
  return noteBox(
    "מבנה העבודה המומלץ",
    `עבדו בשלבים קצרים ומתועדים. התחילו במשימות הפתיחה (${taskNames}), ורק אחרי שכל בדיקת בסיס עוברת המשיכו לשלב הבא. בכל שינוי שמפעיל כלי התקפי או מודל, רשמו מה ציפיתם לראות, מה קרה בפועל, ואיזה מדד מוכיח שהמערכת השתפרה.`,
  );
}

function illustration(pair, kind) {
  const [primary, accent, wash] = palettes[(pair.num - 1) % palettes.length];
  const center = kind === "lecture" ? "AI" : "LAB";
  const labels = {
    1: ["LLM", "MITRE", "SOC", "RAG"],
    2: ["AE", "IForest", "ROC", "Wazuh"],
    3: ["Zeek", "Suricata", "JA3", "C2"],
    4: ["YARA", "EMBER", "CAPA", "Evasion"],
    5: ["UEBA", "AD", "Graph", "DLP"],
    6: ["CTI", "STIX", "MISP", "NER"],
    7: ["URL", "NLP", "Brand", "Mail"],
    8: ["SIEM", "CI/CD", "SOAR", "Agent"],
    9: ["MCP", "PyRIT", "Guard", "Prompt"],
    10: ["SOC", "ML", "LLM", "KPI"],
  }[pair.num];

  const node = (x, y, text, fill = "#ffffff") => `
    <g>
      <rect x="${x}" y="${y}" width="118" height="42" rx="10" fill="${fill}" stroke="${primary}" stroke-width="2"/>
      <text x="${x + 59}" y="${y + 27}" text-anchor="middle" class="svg-label">${escapeHtml(text)}</text>
    </g>`;

  return `<figure class="hero-visual" aria-label="איור נושא למפגש ${pair.num}">
    <svg viewBox="0 0 900 260" role="img" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="g${pair.num}${kind}" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="${wash}"/>
          <stop offset="100%" stop-color="#ffffff"/>
        </linearGradient>
      </defs>
      <rect x="0" y="0" width="900" height="260" rx="22" fill="url(#g${pair.num}${kind})"/>
      <path d="M158 76 C278 22, 348 152, 450 92 S655 36, 748 116" fill="none" stroke="${accent}" stroke-width="4" stroke-linecap="round"/>
      <path d="M160 178 C280 120, 356 212, 468 162 S658 120, 744 188" fill="none" stroke="${primary}" stroke-width="3" stroke-linecap="round" opacity="0.72"/>
      <circle cx="450" cy="132" r="58" fill="${primary}"/>
      <circle cx="450" cy="132" r="44" fill="${accent}" opacity="0.86"/>
      <text x="450" y="142" text-anchor="middle" class="svg-center">${center}</text>
      ${node(64, 38, labels[0])}
      ${node(704, 38, labels[1])}
      ${node(64, 180, labels[2])}
      ${node(704, 180, labels[3])}
      <line x1="182" y1="59" x2="392" y2="114" stroke="${primary}" stroke-width="2.5" opacity="0.55"/>
      <line x1="704" y1="59" x2="508" y2="114" stroke="${primary}" stroke-width="2.5" opacity="0.55"/>
      <line x1="182" y1="201" x2="392" y2="150" stroke="${primary}" stroke-width="2.5" opacity="0.55"/>
      <line x1="704" y1="201" x2="508" y2="150" stroke="${primary}" stroke-width="2.5" opacity="0.55"/>
    </svg>
    <figcaption>${kind === "lecture" ? "מפת מושגים להרצאה" : "מפת זרימת עבודה לתרגול"}</figcaption>
  </figure>`;
}

function css(pair) {
  const [primary, accent, wash] = palettes[(pair.num - 1) % palettes.length];
  return `<style>
    @page { size: A4; margin: 18mm 17mm 20mm; }
    * { box-sizing: border-box; }
    html { direction: rtl; }
    body {
      margin: 0;
      color: #1f2933;
      background: #f6f7f9;
      font-family: Arial, "Noto Sans Hebrew", "Segoe UI", sans-serif;
      font-size: 16px;
      line-height: 1.65;
    }
    .page {
      width: min(100%, 980px);
      margin: 28px auto;
      background: #fff;
      box-shadow: 0 18px 60px rgba(22, 34, 51, 0.12);
      border: 1px solid #e5e7eb;
    }
    header {
      padding: 34px 42px 24px;
      background: ${wash};
      border-bottom: 6px solid ${primary};
    }
    .kicker {
      margin: 0 0 8px;
      color: ${accent};
      font-weight: 700;
      font-size: 14px;
    }
    .term {
      direction: ltr;
      unicode-bidi: isolate;
      display: inline;
    }
    h1 {
      margin: 0;
      color: ${primary};
      font-size: 30px;
      line-height: 1.25;
    }
    .subtitle {
      margin: 12px 0 0;
      color: #52606d;
      font-size: 17px;
      font-weight: 700;
    }
    main { padding: 28px 42px 42px; }
    .hero-visual { margin: 0 0 28px; page-break-inside: avoid; }
    .hero-visual svg { display: block; width: 100%; height: auto; border-radius: 18px; }
    figcaption {
      margin-top: 7px;
      color: #66788a;
      font-size: 13px;
      text-align: center;
    }
    .svg-label {
      fill: ${primary};
      font: 700 17px Arial, sans-serif;
    }
    .svg-center {
      fill: #fff;
      font: 800 26px Arial, sans-serif;
    }
    .lead {
      margin: 0 0 22px;
      padding: 16px 18px;
      border-right: 6px solid ${accent};
      background: #fafafa;
      border-radius: 12px;
      font-weight: 700;
    }
    .intro {
      margin: 0 0 26px;
      padding: 18px 20px;
      border-radius: 16px;
      background: ${wash};
      border: 1px solid #e5e7eb;
    }
    .intro p {
      margin-bottom: 10px;
      font-size: 17px;
    }
    .note-box {
      margin: 0 0 24px;
      padding: 16px 18px;
      border-radius: 14px;
      background: #f8fafc;
      border: 1px solid #d9e2ec;
      page-break-inside: avoid;
    }
    .note-box h2 {
      margin-top: 0;
    }
    .block {
      margin: 0 0 26px;
      page-break-inside: avoid;
    }
    h2 {
      margin: 26px 0 10px;
      color: ${primary};
      font-size: 22px;
      line-height: 1.35;
      border-bottom: 1px solid #d9e2ec;
      padding-bottom: 5px;
    }
    h3 {
      margin: 18px 0 8px;
      color: #334e68;
      font-size: 18px;
      line-height: 1.35;
    }
    p { margin: 0 0 12px; }
    ul, ol { margin: 8px 0 0; padding: 0 24px 0 0; }
    li { margin: 5px 0; }
    .objectives {
      columns: 2;
      column-gap: 32px;
    }
    .section-card {
      margin: 0 0 18px;
      padding: 16px 18px;
      border: 1px solid #e5e7eb;
      border-radius: 14px;
      background: #fff;
      page-break-inside: avoid;
    }
    .section-card p + p {
      margin-top: 8px;
    }
    .task-card {
      margin: 0 0 16px;
      padding: 16px 18px;
      border: 1px solid #d9e2ec;
      border-right: 5px solid ${accent};
      border-radius: 14px;
      background: #fff;
      page-break-inside: avoid;
    }
    .meta-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      margin: 0 0 24px;
    }
    .meta {
      padding: 14px 16px;
      background: #f8fafc;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      page-break-inside: avoid;
    }
    .meta strong { color: ${primary}; display: block; margin-bottom: 4px; }
    .validation {
      margin-top: 10px;
      padding: 10px 12px;
      background: #fff7ed;
      border: 1px solid #fed7aa;
      border-radius: 10px;
      font-weight: 700;
    }
    footer {
      padding: 16px 42px 22px;
      color: #66788a;
      border-top: 1px solid #e5e7eb;
      font-size: 13px;
    }
    @media print {
      body { background: #fff; }
      .page { width: auto; margin: 0; box-shadow: none; border: 0; }
      header, main, footer { padding-right: 0; padding-left: 0; }
      .objectives { columns: 1; }
      a { color: inherit; text-decoration: none; }
    }
    @media (max-width: 720px) {
      header, main, footer { padding-right: 22px; padding-left: 22px; }
      h1 { font-size: 24px; }
      .objectives { columns: 1; }
      .meta-grid { grid-template-columns: 1fr; }
    }
  </style>`;
}

function documentShell(pair, kind, body) {
  return `<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <title>${escapeHtml(kind === "lecture" ? "הרצאה" : "תרגול")} ${pair.num}: ${escapeHtml(pair.title)}</title>
  ${css(pair)}
</head>
<body>
  <article class="page">
    ${body}
  </article>
</body>
</html>
`;
}

function lectureHtml(pair) {
  const sections = pair.lecture.sections.map((section) => `
    <section class="section-card">
      <h2>${richText(section.h)}</h2>
      ${prose(section.p)}
      ${list(section.bullets)}
    </section>`).join("");

  return documentShell(pair, "lecture", `
    <header>
      <p class="kicker">Sprint Tech Academy | AI לאבטחת סייבר</p>
      <h1><span>מפגש ${pair.num}:</span> <span dir="rtl">${richText(pair.title)}</span></h1>
      <p class="subtitle">קובץ הרצאה מעוצב</p>
    </header>
    <main>
      ${illustration(pair, "lecture")}
      <section class="intro">
        ${prose(expansions[pair.num]?.lecture)}
      </section>
      <section class="block">
        <h2>מטרות הלמידה</h2>
        ${list(pair.lecture.objectives, "objectives")}
      </section>
      ${studyPath(pair)}
      ${sections}
      ${labeledList(pair.lecture.refs, "מקורות והפניות")}
    </main>
    <footer>נוצר מתוך קבצי Claude Cowork | מפגש ${pair.num} | הרצאה</footer>`);
}

function exerciseHtml(pair) {
  const tasks = pair.exercise.tasks.map((task) => `
    <section class="task-card">
      <h2>${richText(task.name)}</h2>
      ${list(task.steps)}
      ${task.validate ? `<div class="validation">בדיקה: ${richText(task.validate)}</div>` : ""}
    </section>`).join("");

  return documentShell(pair, "exercise", `
    <header>
      <p class="kicker">Sprint Tech Academy | AI לאבטחת סייבר</p>
      <h1><span>תרגול מפגש ${pair.num}:</span> <span dir="rtl">${richText(pair.title)}</span></h1>
      <p class="subtitle">Hands-On Lab מעוצב ומוכן להדפסה</p>
    </header>
    <main>
      ${illustration(pair, "exercise")}
      <p class="lead">${richText(pair.exercise.objective)}</p>
      <section class="intro">
        ${prose(expansions[pair.num]?.exercise)}
      </section>
      <section class="meta-grid">
        <div class="meta"><strong>משך</strong>${richText(pair.exercise.duration)}</div>
        <div class="meta"><strong>טופולוגיה</strong>${richText(pair.exercise.topology)}</div>
      </section>
      ${exercisePath(pair)}
      ${labeledList(pair.exercise.prereqs, "דרישות מקדימות")}
      ${tasks}
      ${labeledList(pair.exercise.bonus, "בונוס")}
      ${labeledList(pair.exercise.deliverables, "תוצרים להגשה")}
      ${labeledList(pair.exercise.troubleshooting, "Troubleshooting")}
    </main>
    <footer>נוצר מתוך קבצי Claude Cowork | מפגש ${pair.num} | תרגול</footer>`);
}

function indexHtml(generated) {
  const rows = generated.map((entry) => `
    <tr>
      <td>${entry.meeting}</td>
      <td>${richText(entry.title)}</td>
      <td><a href="${entry.lecture}">הרצאה</a></td>
      <td><a href="${entry.exercise}">תרגול</a></td>
    </tr>`).join("");

  return `<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>אינדקס קבצי AI לאבטחת סייבר</title>
  <style>
    body { margin: 0; font-family: Arial, "Noto Sans Hebrew", sans-serif; background: #f6f7f9; color: #1f2933; direction: rtl; }
    main { width: min(100% - 40px, 980px); margin: 36px auto; background: #fff; border: 1px solid #e5e7eb; border-radius: 18px; padding: 32px; box-shadow: 0 18px 60px rgba(22, 34, 51, 0.12); }
    h1 { margin: 0 0 10px; color: #0f4c5c; }
    p { color: #52606d; }
    table { width: 100%; border-collapse: collapse; margin-top: 22px; }
    th, td { padding: 12px 14px; border-bottom: 1px solid #e5e7eb; text-align: right; }
    th { background: #edf7fa; color: #0f4c5c; }
    a { color: #0f4c5c; font-weight: 700; }
  </style>
</head>
<body>
  <main>
    <h1>10 זוגות קבצים מעוצבים: AI לאבטחת סייבר</h1>
    <p>כל קובץ הוא HTML עצמאי עם עיצוב, איור מוטמע, RTL תקין והגדרות הדפסה ל-A4.</p>
    <table>
      <thead><tr><th>מפגש</th><th>נושא</th><th>קובץ הרצאה</th><th>קובץ תרגול</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  </main>
</body>
</html>
`;
}

function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const generated = [];

  for (const pair of pairs) {
    const lecture = slug(pair.num, "lecture");
    const exercise = slug(pair.num, "exercise");
    fs.writeFileSync(path.join(OUT_DIR, lecture), lectureHtml(pair), "utf8");
    fs.writeFileSync(path.join(OUT_DIR, exercise), exerciseHtml(pair), "utf8");
    generated.push({ meeting: pair.num, title: pair.title, lecture, exercise });
  }

  fs.writeFileSync(path.join(OUT_DIR, "index.html"), indexHtml(generated), "utf8");
  fs.writeFileSync(
    path.join(OUT_DIR, "manifest.json"),
    `${JSON.stringify({
      sourceFiles: [
        "claude_cowork_inputs/content_pairs.js",
        "claude_cowork_inputs/build_syllabus.js",
        "claude_cowork_inputs/AI_Cybersecurity_Syllabus_Extended.docx",
      ],
      generatedFiles: generated,
      format: "standalone RTL HTML with embedded SVG illustrations and A4 print styling",
    }, null, 2)}\n`,
    "utf8",
  );

  console.log(`Generated ${generated.length * 2} designed HTML files in ${OUT_DIR}`);
}

main();
