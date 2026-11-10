import os
import sqlite3
import unittest
from unittest.mock import patch

import database


class _FakeCursor:
    def __init__(self):
        self.rows = []
        self.rowcount = -1
        self.description = None
        self.statements = []

    def execute(self, statement, parameters=None):
        self.statements.append((statement, parameters))
        if statement.startswith("SELECT"):
            self.rows = [(7, "visible")]
            self.description = (("id",), ("value",))
            self.rowcount = 1
        elif "RETURNING id" in statement:
            self.rows = [(42,)]
            self.rowcount = 1
        else:
            self.rows = []
            self.rowcount = 0

    def fetchone(self):
        return self.rows.pop(0) if self.rows else None

    def fetchall(self):
        rows, self.rows = self.rows, []
        return rows

    def close(self):
        pass


class _FakeConnection:
    def __init__(self):
        self.cursors = []

    def cursor(self, cursor_factory=None):
        cursor = _FakeCursor()
        self.cursors.append(cursor)
        return cursor

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


class DatabaseConnectionTests(unittest.TestCase):
    def test_non_production_database_path_uses_sqlite(self):
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://db.example/app"}):
            connection = database.connect_database("test_jobs.db")
            try:
                self.assertIsInstance(connection, sqlite3.Connection)
            finally:
                connection.close()

    def test_postgres_select_keeps_result_rows_available(self):
        raw_connection = _FakeConnection()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://db.example/app"}):
            with patch.object(database.psycopg2, "connect", return_value=raw_connection):
                connection = database.connect_database("jobs.db")
                cursor = connection.cursor()
                cursor.execute("SELECT id, value FROM jobs WHERE id = ?", (7,))

        statement_cursor = raw_connection.cursors[0]
        self.assertIn("WHERE id = %s", statement_cursor.statements[0][0])
        row = cursor.fetchone()
        self.assertEqual(row[0], 7)
        self.assertEqual(row["value"], "visible")
        self.assertEqual(dict(row), {"id": 7, "value": "visible"})
        connection.close()

    def test_postgres_insert_supplies_compatible_lastrowid(self):
        raw_connection = _FakeConnection()
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://db.example/app"}):
            with patch.object(database.psycopg2, "connect", return_value=raw_connection):
                connection = database.connect_database("jobs.db")
                cursor = connection.cursor()
                cursor.execute("INSERT INTO users (username) VALUES (?)", ("alice",))

        statement_cursor = raw_connection.cursors[0]
        self.assertIn("VALUES (%s) RETURNING id", statement_cursor.statements[0][0])
        self.assertEqual(cursor.lastrowid, 42)
        connection.close()

    def test_sqlite_specific_schema_checks_are_translated(self):
        pragma = database._translate_statement("PRAGMA table_info(users)")
        sqlite_master = database._translate_statement(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'"
        )
        ignored_insert = database._translate_statement(
            "INSERT OR IGNORE INTO jobs (title) VALUES (?)"
        )

        self.assertIn("information_schema.columns", pragma)
        self.assertIn("information_schema.tables", sqlite_master)
        self.assertIn("ON CONFLICT DO NOTHING", ignored_insert)
        self.assertIn("VALUES (%s)", ignored_insert)


if __name__ == "__main__":
    unittest.main()
