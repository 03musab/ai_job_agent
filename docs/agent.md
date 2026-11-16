# Agent Instructions for AI Job Agent

Welcome! This file provides context and instructions for AI agents working on this project.

## 🏗️ Project Overview

This is an **AI-powered Job Agent** that helps users track jobs, calculate skill gaps, and generate learning paths.

- **Backend**: Python (Flask)
- **Frontend**: HTML templates with Vanilla CSS + Tailwind CSS (via PostCSS/CLI)
- **Services**: `roadmap_service.py`, `skill_gap_service.py`, `relevance_calculator.py`

## 🚀 Common Commands

### Frontend Build

```powershell
# Build Tailwind CSS (one-time)
npm run build:css

# Watch for CSS changes
npm run watch:css
```

### Testing

```powershell
# Run the main test suite
python tests/test_app.py
```

## 🎨 Design System & Aesthetics

- **Premium Focus**: Ensure all UI changes are visually stunning. Use dark modes, glassmorphism, and smooth transitions.
- **Styling**: Favor modern, semantic CSS. Tailwind is available but should be used for layout/utilities while maintaining a clean component structure.
- **Micro-interactions**: Add hover effects and subtle animations to improve the feel of the dashboard.

## 🧠 Development Workflow

1. **Plan FIRST**: Always create/update an `implementation_plan.md` in the agent's brain directory before making changes.
2. **State Tracking**: Maintain a `task.md` to track progress through complex tasks.
3. **Verification**: Always run `tests/test_app.py` after backend changes. For UI changes, use the Browser sub-agent to verify rendering.

---
