"""
Style all lecture.md and EXERCISES.md files in course/ with consistent emoji,
metadata badges, and GitHub callout blocks.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSE = ROOT / "course"

# ── emoji mappings for section headings ──────────────────────────────────────
LECTURE_HEADING_MAP: dict[str, str] = {
    "Learning Objectives": "🎯 Learning Objectives",
    "Session Flow": "🗓 Session Flow",
    "Session Completion Checklist": "✅ Session Completion Checklist",
    "Files in this session": "📁 Files in this session",
    "Coverage Summary": "📊 Coverage Summary",
    "When NOT to Automate": "⚠️ When NOT to Automate",
    "When to Automate": "🤖 When to Automate",
    "Defect Lifecycle": "🐛 Defect Lifecycle",
    "The Test Pyramid": "🔺 The Test Pyramid",
    "Test Pyramid": "🔺 Test Pyramid",
    "Risk-Based Testing": "⚡ Risk-Based Testing",
    "Exploratory Testing": "🔍 Exploratory Testing",
    "Test Design Techniques": "🔬 Test Design Techniques",
    "Test Plan": "📋 Test Plan",
    "What Is a Test Case?": "📝 What Is a Test Case?",
    "What is a Test Case?": "📝 What is a Test Case?",
    "Test Types": "🏷️ Test Types",
    "Key Takeaways": "💡 Key Takeaways",
    "Quick Reference": "📌 Quick Reference",
    "Common Mistakes": "🚫 Common Mistakes",
    "Common Anti-Patterns": "🚫 Common Anti-Patterns",
    "Anti-Patterns": "🚫 Anti-Patterns",
    "Best Practices": "⭐ Best Practices",
    "Prerequisites": "📋 Prerequisites",
    "Summary": "📌 Summary",
    "Architecture": "🏗️ Architecture",
    "Setup": "⚙️ Setup",
    "Configuration": "⚙️ Configuration",
    "How It Works": "⚙️ How It Works",
    "Example": "💡 Example",
    "Examples": "💡 Examples",
    "Exercise": "✏️ Exercise",
    "Further Reading": "📚 Further Reading",
    "Resources": "📚 Resources",
    "References": "📚 References",
    "Notes": "📝 Notes",
    "Tips": "💡 Tips",
    "Debugging": "🔧 Debugging",
    "Troubleshooting": "🔧 Troubleshooting",
}

EXERCISES_HEADING_MAP: dict[str, str] = {
    "How to Submit": "📤 How to Submit",
    "Review Criteria": "✔️ Review Criteria",
    "Submission": "📤 Submission",
    "Grading": "✔️ Grading",
}


def _apply_heading_emoji(text: str, mapping: dict[str, str]) -> str:
    """Replace ## Heading with ## emoji Heading (only exact matches, once each)."""
    for plain, styled in mapping.items():
        emoji = styled.split()[0]
        # {{1,3}} escapes the curly braces so the f-string doesn't swallow them
        pattern = rf"^(#{{1,3}}) (?!.*{re.escape(emoji)}){re.escape(plain)}$"
        text = re.sub(pattern, rf"\1 {styled}", text, flags=re.MULTILINE)
    return text


def _apply_exercise_headings(text: str) -> str:
    """## Exercise N: Title → ## ✏️ Exercise N: Title"""
    return re.sub(
        r"^(#{2,3}) (Exercise \d+:)",
        r"\1 ✏️ \2",
        text,
        flags=re.MULTILINE,
    )


def _apply_callouts(text: str) -> str:
    """
    Convert specific patterns to GitHub alert callouts.
    Only convert clearly tip/warning/note markers to avoid changing content.
    """
    # Bold "Note:" paragraphs → [!NOTE]
    text = re.sub(
        r"^\*\*Note:\*\* (.+)$",
        r"> [!NOTE]\n> \1",
        text,
        flags=re.MULTILINE,
    )
    # Bold "Tip:" paragraphs → [!TIP]
    text = re.sub(
        r"^\*\*Tip:\*\* (.+)$",
        r"> [!TIP]\n> \1",
        text,
        flags=re.MULTILINE,
    )
    # Bold "Warning:" paragraphs → [!WARNING]
    text = re.sub(
        r"^\*\*Warning:\*\* (.+)$",
        r"> [!WARNING]\n> \1",
        text,
        flags=re.MULTILINE,
    )
    # Bold "Important:" paragraphs → [!IMPORTANT]
    text = re.sub(
        r"^\*\*Important:\*\* (.+)$",
        r"> [!IMPORTANT]\n> \1",
        text,
        flags=re.MULTILINE,
    )
    return text


def _add_lecture_badge(text: str, session_dir: Path) -> str:
    """
    Insert a metadata badge line after the first # heading
    if not already present.
    """
    badge = f"> 📚 **Lecture** · [{session_dir.name}](.) · [Learning path](../README.md)"
    lines = text.split("\n")
    # Check if badge already inserted
    if any("> 📚 **Lecture**" in l for l in lines[:5]):
        return text
    # Find first # heading line
    for i, line in enumerate(lines):
        if line.startswith("# "):
            lines.insert(i + 1, "")
            lines.insert(i + 2, badge)
            lines.insert(i + 3, "")
            break
    return "\n".join(lines)


def _add_exercises_badge(text: str, session_dir: Path) -> str:
    """Insert a metadata badge line after the first # heading in EXERCISES.md."""
    badge = f"> ✏️ **Exercises** · [{session_dir.name}](.) · [Lecture notes](lecture.md)"
    lines = text.split("\n")
    if any("> ✏️ **Exercises**" in l for l in lines[:5]):
        return text
    for i, line in enumerate(lines):
        if line.startswith("# "):
            lines.insert(i + 1, "")
            lines.insert(i + 2, badge)
            lines.insert(i + 3, "")
            break
    return "\n".join(lines)


def _normalize_table_separator(text: str) -> str:
    """Normalize |---|---| style separators to |---|---| (already fine mostly)."""
    # Ensure at least 3 dashes per column in separator rows for readability
    def expand_sep(m: re.Match) -> str:
        return re.sub(r"\|-+\|", "|---|", m.group(0))

    return re.sub(r"^\|[-| :]+\|$", expand_sep, text, flags=re.MULTILINE)


def style_lecture(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    session_dir = path.parent
    text = _add_lecture_badge(text, session_dir)
    text = _apply_heading_emoji(text, LECTURE_HEADING_MAP)
    text = _apply_callouts(text)
    path.write_text(text, encoding="utf-8")


def style_exercises(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    session_dir = path.parent
    text = _add_exercises_badge(text, session_dir)
    text = _apply_heading_emoji(text, EXERCISES_HEADING_MAP)
    text = _apply_exercise_headings(text)
    text = _apply_callouts(text)
    path.write_text(text, encoding="utf-8")


def style_readme(path: Path) -> None:
    """Style course/README.md."""
    text = path.read_text(encoding="utf-8")
    # Add badge after title if missing
    badge = "> 🎓 **30-session automation QA course** — pytest · Playwright · Allure · AI tools"
    lines = text.split("\n")
    if not any("> 🎓" in l for l in lines[:5]):
        for i, line in enumerate(lines):
            if line.startswith("# "):
                lines.insert(i + 1, "")
                lines.insert(i + 2, badge)
                lines.insert(i + 3, "")
                break
    text = "\n".join(lines)
    # Apply heading emoji
    readme_map = {
        "Prerequisites": "📋 Prerequisites",
        "Learning Path": "🗺️ Learning Path",
        "Exercise Workflow": "✏️ Exercise Workflow",
        "Git Bridge": "🔀 Git Bridge",
        "Session Order": "🗓 Session Order",
        "How to Use": "⚙️ How to Use",
        "Capstone": "🏆 Capstone",
    }
    text = _apply_heading_emoji(text, readme_map)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    changed = 0
    # course/README.md
    readme = COURSE / "README.md"
    if readme.exists():
        style_readme(readme)
        changed += 1
        print(f"  styled: {readme.relative_to(ROOT)}")

    # session folders
    for session_dir in sorted(COURSE.iterdir()):
        if not session_dir.is_dir():
            continue
        if not session_dir.name.startswith("session_"):
            continue

        lecture = session_dir / "lecture.md"
        exercises = session_dir / "EXERCISES.md"

        if lecture.exists():
            style_lecture(lecture)
            changed += 1
            print(f"  styled: {lecture.relative_to(ROOT)}")

        if exercises.exists():
            style_exercises(exercises)
            changed += 1
            print(f"  styled: {exercises.relative_to(ROOT)}")

    print(f"\nDone — {changed} files styled.")


if __name__ == "__main__":
    main()
