"""
AI JobSnap - Fresh Production Launch Reset Script

Safely wipes all test/account/job/outreach/learning data locally and (optionally)
in PostgreSQL & Redis, then re-initializes clean, empty database schemas.

Dry-run by default: nothing is deleted unless `--confirm-wipe-all` is passed.

Usage:
    # Preview what will be wiped (safe dry run - makes NO changes):
    python scripts/reset_all_data.py --include-postgres

    # Wipe local files/SQLite DBs only:
    python scripts/reset_all_data.py --confirm-wipe-all

    # Wipe BOTH local files AND PostgreSQL (DATABASE_URL) + optional Redis:
    python scripts/reset_all_data.py --include-postgres --flush-redis --confirm-wipe-all

    # Optional: keep global_hiring_contacts table intact in Postgres:
    python scripts/reset_all_data.py --include-postgres --keep-global-contacts --confirm-wipe-all
"""

import argparse
import glob
import os
import shutil
import sqlite3
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT_DIR / ".env")
except Exception:
    pass

# All 25 tables across JobDatabase, OutreachDatabase, and SQLAlchemy Learning Models
ALL_TABLES = [
    # JobDatabase (12)
    "user_reminders",
    "recruiter_notifications",
    "job_applications",
    "companies",
    "user_job_feedback",
    "user_custom_scores",
    "search_profiles",
    "jobs",
    "user_details",
    "email_verification_tokens",
    "password_setup_tokens",
    "users",
    # OutreachDatabase (5)
    "outreach_logs",
    "campaigns",
    "templates",
    "contacts",
    "global_hiring_contacts",
    # Learning Models (8)
    "user_learning_progress",
    "learning_resources",
    "learning_modules",
    "learning_paths",
    "job_match_analysis",
    "generated_roadmap",
    "skill_gap_analysis",
    "user_profile_extended",
]

# Local files to remove (NEVER includes .env, credentials.json, role_skill_map.json, or jobsnap_waitlist_contacts.csv)
LOCAL_FILES = [
    "jobs.db",
    "jobs.db-wal",
    "jobs.db-shm",
    "outreach.db",
    "outreach.db-wal",
    "outreach.db-shm",
    os.path.join("instance", "learning_paths.db"),
    os.path.join("instance", "learning_paths.db-wal"),
    os.path.join("instance", "learning_paths.db-shm"),
    "celerybeat-schedule.bak",
    "celerybeat-schedule.dat",
    "celerybeat-schedule.dir",
    "token.pickle",
]

LOCAL_GLOBS = [
    "*.pre-postgres-*.db",
    os.path.join("instance", "*.pre-postgres-*.db"),
    "jobs_report_*.xlsx",
    os.path.join("static", "learning_resources", "*.pdf"),
]

# Directories whose CONTENTS should be wiped (base directories recreated empty)
WIPE_DIR_CONTENTS = [
    "uploads",
]

ENSURE_EMPTY_DIRS = [
    "uploads",
    os.path.join("uploads", "csv_repository"),
    os.path.join("uploads", "company-logos"),
    os.path.join("static", "learning_resources"),
]


def _safe_db_label(url: str) -> str:
    """Format a database URL without ever printing credentials."""
    parsed = urlparse(url)
    host = parsed.hostname or "unknown-host"
    port = f":{parsed.port}" if parsed.port else ""
    db_name = (parsed.path or "").lstrip("/") or "default"
    return f"{parsed.scheme}://{host}{port}/{db_name}"


def _normalize_pg_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://"):]
    return url


def _count_sqlite_rows(db_path: Path) -> dict:
    counts = {}
    if not db_path.exists():
        return counts
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        for (tbl,) in cur.fetchall():
            try:
                cur.execute(f'SELECT COUNT(*) FROM "{tbl}"')
                counts[tbl] = cur.fetchone()[0]
            except Exception:
                counts[tbl] = "?"
        conn.close()
    except Exception as exc:
        counts["_error"] = str(exc)
    return counts


def _collect_local_targets():
    files_to_remove = []
    seen = set()

    for rel in LOCAL_FILES:
        p = ROOT_DIR / rel
        if p.exists() and p.is_file() and str(p) not in seen:
            files_to_remove.append(p)
            seen.add(str(p))

    for pattern in LOCAL_GLOBS:
        for match in glob.glob(str(ROOT_DIR / pattern)):
            p = Path(match)
            if p.exists() and p.is_file() and str(p) not in seen:
                files_to_remove.append(p)
                seen.add(str(p))

    dir_entries_to_remove = []
    for rel_dir in WIPE_DIR_CONTENTS:
        base = ROOT_DIR / rel_dir
        if base.exists() and base.is_dir():
            for child in sorted(base.iterdir()):
                if child.name == ".gitkeep":
                    continue
                dir_entries_to_remove.append(child)

    return files_to_remove, dir_entries_to_remove


def wipe_local(execute: bool):
    print("\n" + "=" * 68)
    print("1. LOCAL DATA & ARTIFACTS")
    print("=" * 68)

    for db_rel in ["jobs.db", "outreach.db", os.path.join("instance", "learning_paths.db")]:
        db_path = ROOT_DIR / db_rel
        if db_path.exists():
            counts = _count_sqlite_rows(db_path)
            non_zero = {k: v for k, v in counts.items() if v not in (0, "0")}
            print(f"  [SQLite] {db_rel}: {len(counts)} tables, non-empty={non_zero or 'none'}")

    files_to_remove, dir_entries = _collect_local_targets()

    if not files_to_remove and not dir_entries:
        print("  No local database files, tokens, or upload entries found.")
    else:
        for f in files_to_remove:
            rel = f.relative_to(ROOT_DIR)
            if execute:
                f.unlink(missing_ok=True)
                print(f"  [DELETED FILE] {rel}")
            else:
                print(f"  [WOULD DELETE FILE] {rel}")

        for entry in dir_entries:
            rel = entry.relative_to(ROOT_DIR)
            kind = "DIR" if entry.is_dir() else "FILE"
            if execute:
                if entry.is_dir():
                    shutil.rmtree(entry, ignore_errors=False)
                else:
                    entry.unlink(missing_ok=True)
                print(f"  [DELETED {kind}] {rel}")
            else:
                print(f"  [WOULD DELETE {kind}] {rel}")

    if execute:
        for rel_dir in ENSURE_EMPTY_DIRS:
            (ROOT_DIR / rel_dir).mkdir(parents=True, exist_ok=True)
        print("  [OK] Recreated empty upload/resource directories.")


def wipe_postgres(execute: bool, keep_global_contacts: bool):
    print("\n" + "=" * 68)
    print("2. POSTGRESQL DATABASE (DATABASE_URL)")
    print("=" * 68)

    raw_url = (os.environ.get("DATABASE_URL") or "").strip()
    if not raw_url or not raw_url.startswith(("postgres://", "postgresql://")):
        print("  [SKIP] DATABASE_URL is not set to a PostgreSQL URL.")
        return

    pg_url = _normalize_pg_url(raw_url)
    print(f"  Target: {_safe_db_label(pg_url)}")

    try:
        import psycopg2
    except ImportError:
        try:
            import psycopg as psycopg2  # type: ignore
        except ImportError as exc:
            raise RuntimeError("Neither psycopg2 nor psycopg is installed.") from exc

    tables = [t for t in ALL_TABLES if not (keep_global_contacts and t == "global_hiring_contacts")]

    conn = psycopg2.connect(pg_url)
    try:
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                """
            )
            existing = {row[0] for row in cur.fetchall()}

            target_existing = [t for t in tables if t in existing]
            print(f"  Found {len(target_existing)} / {len(tables)} managed tables in public schema:")

            for tbl in target_existing:
                cur.execute(f'SELECT COUNT(*) FROM "{tbl}"')
                cnt = cur.fetchone()[0]
                if cnt > 0 or not execute:
                    print(f"    - {tbl:<28} rows: {cnt}")

            if not execute:
                print("  [DRY RUN] No PostgreSQL tables were modified.")
                conn.rollback()
                return

            if target_existing:
                quoted = ", ".join(f'"{t}"' for t in target_existing)
                cur.execute(f"TRUNCATE TABLE {quoted} RESTART IDENTITY CASCADE")
                conn.commit()
                print(f"  [OK] Truncated {len(target_existing)} PostgreSQL tables (RESTART IDENTITY CASCADE).")

            # Verify 0 rows across all truncated tables
            remaining = {}
            for tbl in target_existing:
                cur.execute(f'SELECT COUNT(*) FROM "{tbl}"')
                cnt = cur.fetchone()[0]
                if cnt != 0:
                    remaining[tbl] = cnt

            if remaining:
                raise RuntimeError(f"Non-zero rows remained after truncate: {remaining}")
            print("  [VERIFIED] All truncated PostgreSQL tables now have 0 rows.")
    finally:
        conn.close()


def flush_redis(execute: bool):
    print("\n" + "=" * 68)
    print("3. REDIS CACHE / BROKER (REDIS_URL)")
    print("=" * 68)

    redis_url = (os.environ.get("REDIS_URL") or os.environ.get("CELERY_BROKER_URL") or "").strip()
    if not redis_url or not redis_url.startswith(("redis://", "rediss://")):
        print("  [SKIP] No REDIS_URL / CELERY_BROKER_URL configured.")
        return

    print(f"  Target: {_safe_db_label(redis_url)}")
    if not execute:
        print("  [DRY RUN] Would execute FLUSHDB on target Redis database.")
        return

    try:
        import redis
    except ImportError:
        print("  [WARN] 'redis' Python package not installed; skipping Redis flush.")
        return

    client = redis.from_url(redis_url)
    client.flushdb()
    print("  [OK] Flushed Redis database.")


def reinitialize_schemas():
    print("\n" + "=" * 68)
    print("4. RE-INITIALIZING CLEAN EMPTY SCHEMAS")
    print("=" * 68)
    from app import initialize_database
    initialize_database()
    print("  [OK] initialize_database() completed - fresh empty schemas ready.")


def main():
    parser = argparse.ArgumentParser(
        description="Reset AI JobSnap local & PostgreSQL data for a fresh production launch."
    )
    parser.add_argument(
        "--confirm-wipe-all",
        action="store_true",
        help="Actually delete files and truncate tables. Without this flag, runs in safe dry-run mode.",
    )
    parser.add_argument(
        "--include-postgres",
        action="store_true",
        help="Also truncate all 25 tables in the PostgreSQL database configured by DATABASE_URL.",
    )
    parser.add_argument(
        "--keep-global-contacts",
        action="store_true",
        help="Preserve the global_hiring_contacts table in PostgreSQL.",
    )
    parser.add_argument(
        "--flush-redis",
        action="store_true",
        help="Also FLUSHDB the Redis instance configured by REDIS_URL.",
    )
    parser.add_argument(
        "--skip-reinit",
        action="store_true",
        help="Do not re-run initialize_database() after wiping.",
    )
    args = parser.parse_args()

    execute = bool(args.confirm_wipe_all)
    mode_banner = "EXECUTE MODE (DESTRUCTIVE WIPE)" if execute else "DRY-RUN PREVIEW (NO CHANGES MADE)"
    print("=" * 68)
    print(f"AI JobSnap Fresh Launch Reset - {mode_banner}")
    print("=" * 68)
    print("Preserved files: .env, credentials.json, role_skill_map.json,")
    print("                 jobsnap_waitlist_contacts.csv, static/assets/, source code")

    wipe_local(execute=execute)

    if args.include_postgres:
        wipe_postgres(execute=execute, keep_global_contacts=args.keep_global_contacts)
    else:
        print("\n[INFO] Skipping PostgreSQL (pass --include-postgres to wipe DATABASE_URL).")

    if args.flush_redis:
        flush_redis(execute=execute)

    if execute and not args.skip_reinit:
        reinitialize_schemas()

    print("\n" + "=" * 68)
    if execute:
        print("RESET COMPLETE. AI JobSnap is 100% clean and ready for fresh signups.")
    else:
        print("DRY RUN COMPLETE. Re-run with --confirm-wipe-all to execute.")
    print("=" * 68)


if __name__ == "__main__":
    main()
