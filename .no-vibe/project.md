---
head: unknown
updated: 2026-11-15
---

## Stack
- Python + Flask, Flask-Login, Flask-SQLAlchemy (`>=3.1.1`), SQLAlchemy (`>=2.0.40`)
- Database: SQLite (`jobs.db`) locally, PostgreSQL (`psycopg2-binary>=2.9.9`) via `database.py` on hosting
- Frontend: Jinja2 templates (`templates/`), Tailwind CSS (`^3.4.1`), vanilla JS + Web Audio API
- Background tasks: Celery + Redis

## Structure
- `app.py`: Main Flask app, `JobDatabase`, `User`, auth/Google OAuth, `/onboarding`, `/api/onboarding/*`, `/profile`, dashboards
- `database.py`: SQLite/PostgreSQL connection & SQL translation compatibility
- `templates/onboarding.html`: 4-step onboarding wizard (`Identity` -> `AI Engine` -> `Velocity` -> `Launch`)
- `templates/base.html`, `templates/profile.html`, `templates/partials/_sidebar.html`: Shared layout and profile UI
- `tests/`: `pytest` + `unittest` suite (`tests/test_app.py`, `tests/test_roadmap_features.py`, `tests/test_pro_invites.py`, `tests/test_proc_runner.py`)

## Conventions
- `JobDatabase` methods use `connect_database(self.db_path)` with `?` placeholders translated to `%s` for PostgreSQL
- Frontend uses Tailwind CSS utility classes + vanilla JS helpers in template `{% block scripts %}`
- Onboarding routes return JSON when `X-Requested-With: XMLHttpRequest` or `request.is_json` is set

## Works
- Google OAuth & JobSnap email/password sign-in redirect first-time users to `/onboarding` and returning users straight to `/dashboard` or `/recruiter/dashboard`
- Step 1 role selection (`seeker` / `recruiter`) + live unique username check (`/api/onboarding/username-check`) & persistence (`/api/onboarding/role`)
- Step 4 multipart submission (`/api/onboarding/complete`) supporting seeker resume upload and recruiter company name
- `pytest` suite passes (56+ tests)

## Open
- Redesigning the onboarding steps in `templates/onboarding.html` (and any supporting routes/tests)
