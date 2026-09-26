from __future__ import annotations

import sqlite3
from pathlib import Path

_VALID_COLUMNS = {"name", "gender", "count", "year"}


def query_by_field(db_path: str | Path, column: str, value: object) -> list[dict[str, object]]:
    if column not in _VALID_COLUMNS:
        raise ValueError(f"Unknown column: {column}")

    database_path = Path(db_path)
    database_uri = f"file:{database_path.as_posix()}?mode=ro"

    with sqlite3.connect(database_uri, uri=True) as connection:
        rows = connection.execute(
            f"SELECT name, gender, count, year FROM names WHERE {column} = ? ORDER BY id",
            (value,),
        ).fetchall()

    return [
        {
            "name": row[0],
            "gender": row[1],
            "count": row[2],
            "year": row[3],
        }
        for row in rows
    ]


def query_by_name(db_path: str | Path, name: str) -> list[dict[str, object]]:
    return query_by_field(db_path, "name", name)


def query_by_year(db_path: str | Path, year: int) -> list[dict[str, object]]:
    return query_by_field(db_path, "year", year)
