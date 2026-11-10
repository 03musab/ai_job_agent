"""Copy the existing SQLite application databases into an empty PostgreSQL database."""

import argparse
import datetime
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SOURCES = {
    "jobs": ROOT / "jobs.db",
    "outreach": ROOT / "outreach.db",
    "learning": ROOT / "instance" / "learning_paths.db",
}


def _source_tables(connection: sqlite3.Connection) -> List[str]:
    return [
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]


def _snapshot(source: Path) -> Path:
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    backup = source.with_name(f"{source.stem}.pre-postgres-{timestamp}{source.suffix}")
    source_connection = sqlite3.connect(source)
    backup_connection = sqlite3.connect(backup)
    try:
        source_connection.backup(backup_connection)
    finally:
        backup_connection.close()
        source_connection.close()
    return backup


def _resolve_order(sources: Dict[str, Tuple[sqlite3.Connection, List[str]]]) -> List[Tuple[str, str]]:
    entries = [(source_name, table) for source_name, (_, tables) in sources.items() for table in tables]
    table_sources: Dict[str, str] = {}
    for source_name, table in entries:
        if table in table_sources:
            raise RuntimeError(
                f"Table {table!r} exists in both {table_sources[table]} and {source_name}; "
                "merge it explicitly before migrating."
            )
        table_sources[table] = source_name

    dependencies: Dict[str, set] = {table: set() for _, table in entries}
    for source_name, table in entries:
        source_connection = sources[source_name][0]
        for foreign_key in source_connection.execute(f'PRAGMA foreign_key_list("{table}")'):
            referenced_table = foreign_key[2]
            if referenced_table in dependencies and referenced_table != table:
                dependencies[table].add(referenced_table)

    ordered = []
    remaining = set(dependencies)
    while remaining:
        ready = sorted(table for table in remaining if not (dependencies[table] & remaining))
        if not ready:
            raise RuntimeError(f"Unable to order SQLite tables because of a foreign-key cycle: {sorted(remaining)}")
        for table in ready:
            ordered.append((table_sources[table], table))
            remaining.remove(table)
    return ordered


def _target_columns(cursor, table: str) -> Dict[str, str]:
    cursor.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_schema = current_schema() AND table_name = %s",
        (table,),
    )
    return {name: data_type for name, data_type in cursor.fetchall()}


def _convert_value(value, target_type: str):
    if value is None:
        return None
    if target_type == "boolean":
        return bool(value)
    if target_type in ("json", "jsonb") and isinstance(value, str):
        return Json(json.loads(value))
    return value


def _copy_table(cursor, source: sqlite3.Connection, table: str) -> int:
    target_columns = _target_columns(cursor, table)
    source_columns = [
        row[1] for row in source.execute(f'PRAGMA table_info("{table}")')
    ]
    unknown_columns = set(source_columns) - set(target_columns)
    if unknown_columns:
        raise RuntimeError(
            f"PostgreSQL table {table!r} is missing SQLite columns: {sorted(unknown_columns)}"
        )

    quoted_table = sql.Identifier(table)
    quoted_columns = sql.SQL(", ").join(sql.Identifier(name) for name in source_columns)
    placeholders = sql.SQL(", ").join(sql.Placeholder() for _ in source_columns)
    insert = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        quoted_table, quoted_columns, placeholders
    )
    source_cursor = source.execute(f'SELECT * FROM "{table}"')
    copied = 0
    while True:
        rows = source_cursor.fetchmany(500)
        if not rows:
            break
        values = [
            tuple(
                _convert_value(row[index], target_columns[column])
                for index, column in enumerate(source_columns)
            )
            for row in rows
        ]
        cursor.executemany(insert, values)
        copied += len(values)
    return copied


def _reset_id_sequence(cursor, table: str):
    cursor.execute("SELECT pg_get_serial_sequence(%s, 'id')", (table,))
    sequence = cursor.fetchone()[0]
    if not sequence:
        return
    statement = sql.SQL(
        "SELECT setval(%s::regclass, GREATEST(COALESCE(MAX(id), 1), 1), COUNT(*) > 0) FROM {}"
    ).format(sql.Identifier(table))
    cursor.execute(statement, (sequence,))


def migrate(source_paths: Dict[str, Path], database_url: str):
    sources = {}
    backups = []
    for name, path in source_paths.items():
        if not path.exists():
            continue
        backup = _snapshot(path)
        backups.append(backup)
        connection = sqlite3.connect(path)
        tables = _source_tables(connection)
        if tables:
            sources[name] = (connection, tables)
        else:
            connection.close()

    if not sources:
        raise RuntimeError("No SQLite database files with application tables were found.")

    from app import JobDatabase, OutreachDatabase, initialize_database

    initialize_database()
    JobDatabase().init_db()
    OutreachDatabase().init_db()

    target = psycopg2.connect(database_url)
    try:
        cursor = target.cursor()
        ordered_tables = _resolve_order(sources)

        for _, table in ordered_tables:
            cursor.execute(
                sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table))
            )
            existing_count = cursor.fetchone()[0]
            if existing_count:
                raise RuntimeError(
                    f"Target table {table!r} already contains {existing_count} rows; "
                    "migration requires an empty target."
                )

        copied_counts = {}
        for source_name, table in ordered_tables:
            source = sources[source_name][0]
            copied_counts[table] = _copy_table(cursor, source, table)
        for _, table in ordered_tables:
            _reset_id_sequence(cursor, table)
        for table, copied in copied_counts.items():
            cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table)))
            actual = cursor.fetchone()[0]
            if actual != copied:
                raise RuntimeError(
                    f"Verification failed for {table}: copied {copied} rows but found {actual}."
                )
        target.commit()
        for table, copied in copied_counts.items():
            print(f"{table}: {copied} rows verified")
        print("SQLite-to-PostgreSQL migration completed.")
        print("SQLite backups:")
        for backup in backups:
            print(f"  {backup}")
    except Exception:
        target.rollback()
        raise
    finally:
        target.close()
        for connection, _ in sources.values():
            connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs-db", type=Path, default=SOURCES["jobs"])
    parser.add_argument("--outreach-db", type=Path, default=SOURCES["outreach"])
    parser.add_argument("--learning-db", type=Path, default=SOURCES["learning"])
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required confirmation to copy data into an empty PostgreSQL database.",
    )
    args = parser.parse_args()

    database_url = os.environ.get("DATABASE_URL")
    if not database_url or not database_url.startswith(("postgres://", "postgresql://")):
        parser.error("Set DATABASE_URL to the Render PostgreSQL connection string.")
    if not args.confirm:
        parser.error("Pass --confirm after verifying the target PostgreSQL database is empty.")

    migrate(
        {
            "jobs": args.jobs_db,
            "outreach": args.outreach_db,
            "learning": args.learning_db,
        },
        database_url,
    )


if __name__ == "__main__":
    main()
