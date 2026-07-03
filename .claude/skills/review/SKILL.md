---
name: review
description: How to review test/automation changes in this repo — priorities, finding format, and pre-checks. Use when reviewing a diff or PR of tests or framework code.
---

# Review Skill

- Prioritize test isolation, flake risk, CI reproducibility, secret handling, retry safety, and report/debug quality.
- Review findings should include file and line references, severity, impact, and a concrete fix.
- Run collection before broad execution: `pytest --collect-only -q`.
