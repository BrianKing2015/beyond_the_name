from __future__ import annotations

import sqlite3
from pathlib import Path


def create_names_database(documents_dir: str | Path) -> Path:
    documents_path = Path(documents_dir)
    documents_path.mkdir(parents=True, exist_ok=True)

    db_path = documents_path / "names.db"

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS names (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gender TEXT NOT NULL,
                count INTEGER NOT NULL,
                year INTEGER
            )
            """
        )

    return db_path


def insert_name_records(db_path: str | Path, records: list[dict[str, object]]) -> None:
    database_path = Path(db_path)

    required_fields = {"name", "gender", "count"}

    with sqlite3.connect(database_path) as connection:
        connection.execute("DELETE FROM names")
        connection.execute("DELETE FROM sqlite_sequence WHERE name = 'names'")

        for record in records:
            missing_fields = sorted(required_fields - set(record))
            if missing_fields:
                raise ValueError(
                    "Invalid record schema: expected fields name, gender, count; missing "
                    f"{', '.join(missing_fields)}"
                )

            connection.execute(
                """
                INSERT INTO names (name, gender, count, year)
                VALUES (?, ?, ?, ?)
                """,
                (
                    record["name"],
                    record["gender"],
                    record["count"],
                    record.get("year"),
                ),
            )
