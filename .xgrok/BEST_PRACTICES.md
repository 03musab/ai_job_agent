# Best practices (project-aware)

Stack signals: **Node.js, pip**  
Languages: **JavaScript/TypeScript, Python**

## For humans + Grok
- Small, reviewable changes.
- Tests for non-trivial logic.
- Document public entrypoints and env vars in README.
- Keep AGENTS.md in sync when layout/commands change.

## Stack notes
- Use package.json scripts; lockfile when adding deps.
- Prefer TypeScript strict if tsconfig exists.
- Prefer virtualenv; pin deps in pyproject/requirements.


