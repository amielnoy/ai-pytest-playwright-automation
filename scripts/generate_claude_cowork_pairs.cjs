const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "..");
const SOURCE_DIR = path.join(ROOT, "claude_cowork_inputs");
const OUT_DIR = path.join(ROOT, "claude_cowork_pairs");

function loadCommonJsData(filePath) {
  const code = fs.readFileSync(filePath, "utf8");
  const sandbox = {
    module: { exports: {} },
    exports: {},
    require,
    console,
  };
  vm.runInNewContext(code, sandbox, { filename: filePath });
  return sandbox.module.exports;
}

const pairs = loadCommonJsData(path.join(SOURCE_DIR, "content_pairs.js"));

function slug(num, kind) {
  return `meeting_${String(num).padStart(2, "0")}_${kind}.md`;
}

function list(items) {
  if (!items || items.length === 0) return "";
  return items.map((item) => `- ${item}`).join("\n");
}

function sectionList(sections) {
  return sections
    .map((section) => {
      const lines = [`## ${section.h}`, "", section.p || ""];
      if (section.bullets && section.bullets.length > 0) {
        lines.push("", ...section.bullets.map((bullet) => `- ${bullet}`));
      }
      return lines.join("\n");
    })
    .join("\n\n");
}

function taskList(tasks) {
  return tasks
    .map((task) => {
      const lines = [`## ${task.name}`];
      if (task.steps && task.steps.length > 0) {
        lines.push("", ...task.steps.map((step) => `- ${step}`));
      }
      if (task.validate) {
        lines.push("", `**Validation:** ${task.validate}`);
      }
      return lines.join("\n");
    })
    .join("\n\n");
}

function lectureMarkdown(pair) {
  const lecture = pair.lecture;
  return [
    `# מפגש ${pair.num}: ${pair.title}`,
    "",
    "## מטרות",
    "",
    list(lecture.objectives),
    "",
    sectionList(lecture.sections),
    "",
    "## מקורות",
    "",
    list(lecture.refs),
    "",
  ].join("\n");
}

function exerciseMarkdown(pair) {
  const exercise = pair.exercise;
  const blocks = [
    `# תרגול מפגש ${pair.num}: ${pair.title}`,
    "",
    `**משך:** ${exercise.duration || ""}`,
    "",
    "## יעד",
    "",
    exercise.objective || "",
    "",
    "## דרישות מקדימות",
    "",
    list(exercise.prereqs),
    "",
    "## טופולוגיה",
    "",
    exercise.topology || "",
    "",
    taskList(exercise.tasks),
  ];

  for (const [title, values] of [
    ["בונוס", exercise.bonus],
    ["תוצרים להגשה", exercise.deliverables],
    ["Troubleshooting", exercise.troubleshooting],
  ]) {
    if (values && values.length > 0) {
      blocks.push("", `## ${title}`, "", list(values));
    }
  }

  blocks.push("");
  return blocks.join("\n");
}

function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });

  const manifest = [];
  for (const pair of pairs) {
    const lectureFile = slug(pair.num, "lecture");
    const exerciseFile = slug(pair.num, "exercise");

    fs.writeFileSync(path.join(OUT_DIR, lectureFile), lectureMarkdown(pair), "utf8");
    fs.writeFileSync(path.join(OUT_DIR, exerciseFile), exerciseMarkdown(pair), "utf8");

    manifest.push({
      meeting: pair.num,
      title: pair.title,
      lecture: lectureFile,
      exercise: exerciseFile,
    });
  }

  fs.writeFileSync(
    path.join(OUT_DIR, "manifest.json"),
    `${JSON.stringify({
      sourceFiles: [
        "claude_cowork_inputs/content_pairs.js",
        "claude_cowork_inputs/build_syllabus.js",
        "claude_cowork_inputs/AI_Cybersecurity_Syllabus_Extended.docx",
      ],
      generatedFiles: manifest,
    }, null, 2)}\n`,
    "utf8",
  );

  console.log(`Generated ${pairs.length * 2} pair files in ${OUT_DIR}`);
}

main();
