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
    database_path = Path(db_path)
    database_uri = f"file:{database_path.as_posix()}?mode=ro"

    with sqlite3.connect(database_uri, uri=True) as connection:
        if "%" in name or "_" in name:
            rows = connection.execute(
                "SELECT name, gender, count, year FROM names WHERE name LIKE ? ORDER BY id",
                (name,),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT name, gender, count, year FROM names WHERE name = ? ORDER BY id",
                (name,),
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


def query_top_names_by_year(
    db_path: str | Path,
    year: int,
    limit: int = 10,
    gender: str | None = None,
) -> list[dict[str, object]]:
    if limit <= 0:
        raise ValueError("limit must be greater than 0")

    if gender is not None:
        gender = gender.upper()
        if gender not in {"F", "M"}:
            raise ValueError("gender must be 'F', 'M', or None")

    database_path = Path(db_path)
    database_uri = f"file:{database_path.as_posix()}?mode=ro"

    query = "SELECT name, gender, count, year FROM names WHERE year = ?"
    params: list[object] = [year]

    if gender is not None:
        query += " AND gender = ?"
        params.append(gender)

    query += " ORDER BY count DESC, name ASC LIMIT ?"
    params.append(limit)

    with sqlite3.connect(database_uri, uri=True) as connection:
        rows = connection.execute(query, params).fetchall()

    return [
        {
            "name": row[0],
            "gender": row[1],
            "count": row[2],
            "year": row[3],
        }
        for row in rows
    ]


def query_name_timeline(db_path: str | Path, name: str) -> dict[str, object]:
    database_path = Path(db_path)
    database_uri = f"file:{database_path.as_posix()}?mode=ro"

    with sqlite3.connect(database_uri, uri=True) as connection:
        row = connection.execute(
            """
            SELECT min(year) AS first_year,
                   (
                       SELECT year
                       FROM names
                       WHERE name = ?
                       ORDER BY count DESC, year ASC
                       LIMIT 1
                   ) AS peak_year,
                   (
                       SELECT count
                       FROM names
                       WHERE name = ?
                       ORDER BY count DESC, year ASC
                       LIMIT 1
                   ) AS peak_count
            FROM names
            WHERE name = ?
            """,
            (name, name, name),
        ).fetchone()

    if row is None or row[0] is None:
        return {}

    first_year, peak_year, peak_count = row
    return {
        "name": name,
        "first_year": first_year,
        "peak_year": peak_year,
        "peak_count": peak_count,
    }


def query_by_year(db_path: str | Path, year: int) -> list[dict[str, object]]:
    return query_by_field(db_path, "year", year)
