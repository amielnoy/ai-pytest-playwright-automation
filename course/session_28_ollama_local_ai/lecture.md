# Session 28 - Ollama Local AI For QA Automation

## Learning Objectives

By the end of this session you will be able to:

- Explain when local AI through Ollama is useful for QA automation.
- Choose a local model profile for summaries, test ideas, failure classification, or small diff review.
- Run an Ollama command safely from the terminal.
- Keep secrets and private customer data out of local model prompts.
- Verify local model output with deterministic tests and source evidence.
- Define fallback behavior when local model quality is not enough.

---

## Why Use Ollama

Ollama runs local models on your machine. For QA teams, this is useful when you want fast local assistance without sending project context to an external hosted model.

Good use cases:

- summarize a short failure log
- generate exploratory test ideas
- classify a traceback into likely cause buckets
- review a small diff for obvious test risks
- rewrite a QA note or bug report draft

Poor use cases:

- replacing pytest assertions
- making release decisions
- reviewing large unscoped repositories
- handling secrets, credentials, or private customer data

---

## Basic Commands

Install and pull a model outside the test suite:

```bash
ollama pull llama3.1
ollama pull qwen2.5-coder
```

Run a prompt:

```bash
ollama run llama3.1 "Suggest edge cases for cart quantity validation"
```

The course examples do not require Ollama to be installed. They model the workflow and command construction only.

---

## Model Selection

| Task | Suggested model | Why |
|---|---|---|
| Summarize QA notes | `llama3.1` | Good general-purpose local reasoning. |
| Generate test ideas | `llama3.1` | Useful for broad scenario lists. |
| Classify failures | `qwen2.5-coder` | Better with code and tracebacks. |
| Review small diffs | `qwen2.5-coder` | Better at code-shaped context. |

Always verify model output against the repo and test results.

---

## Privacy Rule

Do not put these into local model prompts:

- passwords
- API keys
- session cookies
- customer data
- private business data that is not approved for local processing

Local is not automatically safe. Treat it as another tool with explicit data rules.

---

## Runnable Example

```bash
python course/session_28_ollama_local_ai/lecture.py
pytest course/session_28_ollama_local_ai -q
```

The reusable reference implementation lives in `course/framework/ollama/`.

---

## Session Completion Checklist

- [ ] I can explain when Ollama is useful and when it is not.
- [ ] I can choose a model for summaries, test ideas, failure classification, and small diff review.
- [ ] I can write a safe local prompt without secrets.
- [ ] I can turn useful model output into deterministic tests or code.
- [ ] I can define fallback behavior when the local model is weak.
- [ ] I completed the exercises in `EXERCISES.md`.
