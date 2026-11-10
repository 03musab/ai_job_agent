import sqlite3
import tempfile
import unittest
from pathlib import Path

from psycopg2.extras import Json

from scripts import migrate_sqlite_to_postgres as migration


class MigrationHelperTests(unittest.TestCase):
    def test_source_tables_excludes_sqlite_internal_tables(self):
        connection = sqlite3.connect(":memory:")
        connection.execute("CREATE TABLE example (id INTEGER PRIMARY KEY)")

        self.assertEqual(migration._source_tables(connection), ["example"])
        connection.close()

    def test_resolve_order_respects_foreign_keys_across_source_files(self):
        parent = sqlite3.connect(":memory:")
        child = sqlite3.connect(":memory:")
        parent.execute("CREATE TABLE parent (id INTEGER PRIMARY KEY)")
        child.execute(
            "CREATE TABLE child (id INTEGER PRIMARY KEY, "
            "parent_id INTEGER REFERENCES parent(id))"
        )

        ordered = migration._resolve_order(
            {
                "jobs": (parent, ["parent"]),
                "outreach": (child, ["child"]),
            }
        )

        self.assertEqual(ordered, [("jobs", "parent"), ("outreach", "child")])
        parent.close()
        child.close()

    def test_resolve_order_rejects_duplicate_table_names(self):
        first = sqlite3.connect(":memory:")
        second = sqlite3.connect(":memory:")

        with self.assertRaisesRegex(RuntimeError, "exists in both"):
            migration._resolve_order(
                {"jobs": (first, ["users"]), "outreach": (second, ["users"])}
            )
        first.close()
        second.close()

    def test_resolve_order_rejects_foreign_key_cycles(self):
        connection = sqlite3.connect(":memory:")
        connection.execute(
            "CREATE TABLE first_table (id INTEGER PRIMARY KEY, "
            "second_id INTEGER REFERENCES second_table(id))"
        )
        connection.execute(
            "CREATE TABLE second_table (id INTEGER PRIMARY KEY, "
            "first_id INTEGER REFERENCES first_table(id))"
        )

        with self.assertRaisesRegex(RuntimeError, "foreign-key cycle"):
            migration._resolve_order(
                {"jobs": (connection, ["first_table", "second_table"])}
            )
        connection.close()

    def test_convert_value_handles_booleans_and_json(self):
        converted_json = migration._convert_value('{"enabled": true}', "jsonb")

        self.assertIs(migration._convert_value(0, "boolean"), False)
        self.assertIs(migration._convert_value(1, "boolean"), True)
        self.assertIsInstance(converted_json, Json)
        self.assertEqual(converted_json.adapted, {"enabled": True})

    def test_snapshot_creates_distinct_backups_with_the_data(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "jobs.db"
            connection = sqlite3.connect(source)
            try:
                connection.execute("CREATE TABLE jobs (id INTEGER PRIMARY KEY)")
                connection.execute("INSERT INTO jobs (id) VALUES (7)")
                connection.commit()
            finally:
                connection.close()

            first_backup = migration._snapshot(source)
            second_backup = migration._snapshot(source)

            self.assertNotEqual(first_backup, second_backup)
            for backup in (first_backup, second_backup):
                connection = sqlite3.connect(backup)
                try:
                    self.assertEqual(
                        connection.execute("SELECT id FROM jobs").fetchall(),
                        [(7,)],
                    )
                finally:
                    connection.close()


if __name__ == "__main__":
    unittest.main()
