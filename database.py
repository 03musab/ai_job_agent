"""Database connection compatibility for local SQLite and hosted PostgreSQL."""

import os
import re
import sqlite3
from typing import Any, Iterable, Optional, Sequence

import psycopg2
from psycopg2.extras import DictCursor


_SQLITE_PATHS = {"jobs.db", "outreach.db"}


def _postgres_url() -> Optional[str]:
    url = os.environ.get("DATABASE_URL")
    if not url:
        return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql+psycopg2://"):
        url = url.replace("postgresql+psycopg2://", "postgresql://", 1)
    if url.startswith("postgresql+psycopg://"):
        url = url.replace("postgresql+psycopg://", "postgresql://", 1)
    if url.startswith("sqlite:"):
        return None
    if not url.startswith("postgresql://"):
        raise RuntimeError("DATABASE_URL must use SQLite or PostgreSQL.")
    return url


def _replace_placeholders(statement: str) -> str:
    output = []
    quote = None
    index = 0
    while index < len(statement):
        char = statement[index]
        if quote:
            output.append(char)
            if char == quote:
                if index + 1 < len(statement) and statement[index + 1] == quote:
                    output.append(statement[index + 1])
                    index += 1
                else:
                    quote = None
        elif char in ("'", '"'):
            quote = char
            output.append(char)
        elif char == "?":
            output.append("%s")
        else:
            output.append(char)
        index += 1
    return "".join(output)


def _translate_like_to_ilike(statement: str) -> str:
    """Translate SQLite case-insensitive LIKE operators outside quotes to PostgreSQL ILIKE."""
    parts = re.split(r"('(?:''|[^'])*'|\"(?:\"\"|[^\"])*\")", statement)
    for idx in range(0, len(parts), 2):
        parts[idx] = re.sub(r"\bNOT\s+LIKE\b", "NOT ILIKE", parts[idx], flags=re.I)
        parts[idx] = re.sub(r"\bLIKE\b", "ILIKE", parts[idx], flags=re.I)
    return "".join(parts)


def _translate_statement(statement: str) -> str:
    pragma = re.fullmatch(r"\s*PRAGMA\s+table_info\((\w+)\)\s*;?\s*", statement, re.I)
    if pragma:
        table_name = pragma.group(1).lower()
        return (
            "SELECT ordinal_position - 1 AS cid, column_name AS name "
            "FROM information_schema.columns "
            "WHERE table_schema = current_schema() AND table_name = "
            f"'{table_name}' ORDER BY ordinal_position"
        )

    if re.search(r"FROM\s+sqlite_master\b", statement, re.I):
        return re.sub(
            r"SELECT\s+name\s+FROM\s+sqlite_master\s+WHERE\s+type\s*=\s*'table'\s+AND\s+name\s*=\s*'([^']+)'",
            "SELECT table_name AS name FROM information_schema.tables "
            "WHERE table_schema = current_schema() AND table_name = '\\1'",
            statement,
            flags=re.I,
        )

    statement = re.sub(
        r"\bINTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b",
        "SERIAL PRIMARY KEY",
        statement,
        flags=re.I,
    )
    ignore_conflicts = bool(re.match(r"\s*INSERT\s+OR\s+IGNORE\s+INTO\b", statement, re.I))
    statement = re.sub(
        r"\bINSERT\s+OR\s+IGNORE\s+INTO\b",
        "INSERT INTO",
        statement,
        flags=re.I,
    )
    if ignore_conflicts and not re.search(r"\bON\s+CONFLICT\b", statement, re.I):
        statement = statement.rstrip().rstrip(";") + " ON CONFLICT DO NOTHING"
    statement = _translate_like_to_ilike(statement)
    return _replace_placeholders(statement)


class _PostgresCursor:
    def __init__(self, connection: "_PostgresConnection"):
        self._raw = connection._raw.cursor(cursor_factory=DictCursor)
        self._connection = connection
        self.lastrowid = None

    def execute(self, statement: str, parameters: Optional[Sequence[Any]] = None):
        translated = _translate_statement(statement)
        insert_match = re.match(r"\s*INSERT\s+INTO\s+([a-z_][a-z0-9_]*)\b", translated, re.I)
        is_insert = insert_match is not None
        returning_column = "user_id" if insert_match and insert_match.group(1).lower() == "user_details" else "id"
        if is_insert and not re.search(r"\bRETURNING\b", translated, re.I):
            translated = translated.rstrip().rstrip(";") + f" RETURNING {returning_column}"

        self.lastrowid = None
        savepoint = self._connection._next_savepoint()
        self._connection._execute_control(f"SAVEPOINT {savepoint}")
        try:
            self._raw.execute(translated, parameters)
            if is_insert and re.search(rf"\bRETURNING\s+{returning_column}\b", translated, re.I):
                inserted = self._raw.fetchone()
                if inserted is not None:
                    self.lastrowid = inserted[0]
            self._connection._execute_control(f"RELEASE SAVEPOINT {savepoint}")
        except psycopg2.Error as error:
            self._connection._execute_control(f"ROLLBACK TO SAVEPOINT {savepoint}")
            self._connection._execute_control(f"RELEASE SAVEPOINT {savepoint}")
            if isinstance(error, psycopg2.IntegrityError):
                raise sqlite3.IntegrityError(str(error)) from error
            if isinstance(error, (psycopg2.OperationalError, psycopg2.ProgrammingError)):
                raise sqlite3.OperationalError(str(error)) from error
            raise sqlite3.DatabaseError(str(error)) from error
        return self

    def executemany(self, statement: str, parameter_rows: Iterable[Sequence[Any]]):
        for parameters in parameter_rows:
            self.execute(statement, parameters)
        return self

    def fetchone(self):
        row = self._raw.fetchone()
        return self._compatible_row(row)

    def fetchall(self):
        return [self._compatible_row(row) for row in self._raw.fetchall()]

    def _compatible_row(self, row):
        if row is None:
            return None
        columns = [column[0] for column in self._raw.description]
        return _CompatibleRow(row, columns)

    @property
    def rowcount(self):
        return self._raw.rowcount

    @property
    def description(self):
        return self._raw.description

    def close(self):
        self._raw.close()


class _CompatibleRow(list):
    def __init__(self, values, columns):
        super().__init__(values)
        self._columns = columns
        self._column_indexes = {name: index for index, name in enumerate(columns)}

    def __getitem__(self, key):
        if isinstance(key, str):
            key = self._column_indexes[key]
        return super().__getitem__(key)

    def keys(self):
        return self._columns


class _PostgresConnection:
    def __init__(self, url: str, timeout: int):
        self._raw = psycopg2.connect(
            url,
            connect_timeout=timeout,
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5,
        )
        self._savepoint_counter = 0
        self._row_factory = None

    def _next_savepoint(self) -> str:
        self._savepoint_counter += 1
        return f"app_statement_{self._savepoint_counter}"

    def _execute_control(self, statement: str):
        cursor = self._raw.cursor()
        try:
            cursor.execute(statement)
        finally:
            cursor.close()

    def cursor(self):
        return _PostgresCursor(self)

    def commit(self):
        self._raw.commit()

    def rollback(self):
        self._raw.rollback()

    def close(self):
        self._raw.close()

    @property
    def row_factory(self):
        return self._row_factory

    @row_factory.setter
    def row_factory(self, value):
        self._row_factory = value


def connect_database(database_path: str, timeout: int = 10, **kwargs):
    """Connect to Render PostgreSQL for application databases, otherwise use SQLite."""
    url = _postgres_url()
    if url and os.path.basename(os.fspath(database_path)) in _SQLITE_PATHS:
        return _PostgresConnection(url, timeout)
    return sqlite3.connect(database_path, timeout=timeout, **kwargs)


def is_postgres_configured() -> bool:
    return _postgres_url() is not None
