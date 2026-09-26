from pathlib import Path

import sqlite3

from src.sqlite_loader import create_names_database, insert_name_records


def test_sqlite_loader_creates_database_and_tables(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    db_path = create_names_database(documents_dir)

    assert db_path == documents_dir / "names.db"
    assert db_path.exists()


def test_sqlite_loader_inserts_rows_from_csv_records(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    db_path = create_names_database(documents_dir)
    records = [
        {"name": "Mary", "gender": "F", "count": 7065},
        {"name": "John", "gender": "M", "count": 9655},
    ]

    insert_name_records(db_path, records)

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT name, gender, count, year FROM names ORDER BY id"
        ).fetchall()

    assert rows == [
        ("Mary", "F", 7065, None),
        ("John", "M", 9655, None),
    ]


def test_sqlite_loader_add_year(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    db_path = create_names_database(documents_dir)
    records = [
        {"name": "Mary", "gender": "F", "count": 7065, "year": 1880},
        {"name": "John", "gender": "M", "count": 9655, "year": 1880},
    ]

    insert_name_records(db_path, records)

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT name, gender, count, year FROM names ORDER BY id"
        ).fetchall()

    assert rows == [
        ("Mary", "F", 7065, 1880),
        ("John", "M", 9655, 1880),
    ]


def test_sqlite_loader_inserts_rows_from_yob_file(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    yob_file = documents_dir / "yob1880.txt"
    yob_file.write_text("Mary,F,7065\nJohn,M,9655\n", encoding="utf-8")

    db_path = create_names_database(documents_dir)

    from src.csv_reader import read_yob_file
    records = read_yob_file(yob_file)
    for record in records:
        record["year"] = 1880

    insert_name_records(db_path, records)

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT name, gender, count, year FROM names ORDER BY id"
        ).fetchall()

    assert rows == [
        ("Mary", "F", 7065, 1880),
        ("John", "M", 9655, 1880),
    ]


def test_sqlite_loader_replaces_existing_data_cleanly(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    db_path = create_names_database(documents_dir)
    insert_name_records(
        db_path,
        [
            {"name": "Mary", "gender": "F", "count": 7065, "year": 1880},
            {"name": "John", "gender": "M", "count": 9655, "year": 1880},
        ],
    )

    insert_name_records(
        db_path,
        [
            {"name": "Emma", "gender": "F", "count": 1987, "year": 2020},
        ],
    )

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT name, gender, count, year FROM names ORDER BY id"
        ).fetchall()

    assert rows == [
        ("Emma", "F", 1987, 2020),
    ]


def test_sqlite_loader_handles_empty_record_set(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    db_path = create_names_database(documents_dir)
    insert_name_records(db_path, [])

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT COUNT(*) FROM names"
        ).fetchone()[0]

    assert rows == 0


def test_sqlite_loader_rejects_invalid_schema_data(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    db_path = create_names_database(documents_dir)
    invalid_records = [
        {"name": "Mary", "count": 7065},
    ]

    try:
        insert_name_records(db_path, invalid_records)
        raise AssertionError("Expected ValueError for invalid schema record")
    except ValueError as exc:
        assert "name, gender, count" in str(exc)
