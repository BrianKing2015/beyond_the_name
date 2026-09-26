import sqlite3

from src.sqlite_loader import create_names_database, insert_name_records


def test_query_helpers_returns_rows_for_name_lookup(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    db_path = create_names_database(documents_dir)
    insert_name_records(
        db_path,
        [
            {"name": "Mary", "gender": "F", "count": 7065, "year": 1880},
            {"name": "John", "gender": "M", "count": 9655, "year": 1880},
            {"name": "Mary", "gender": "F", "count": 1987, "year": 2020},
        ],
    )

    from src.query_helpers import query_by_name

    rows = query_by_name(db_path, "Mary")

    assert rows == [
        {"name": "Mary", "gender": "F", "count": 7065, "year": 1880},
        {"name": "Mary", "gender": "F", "count": 1987, "year": 2020},
    ]


def test_query_helpers_returns_rows_for_year_filter(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    db_path = create_names_database(documents_dir)
    insert_name_records(
        db_path,
        [
            {"name": "Mary", "gender": "F", "count": 7065, "year": 1880},
            {"name": "John", "gender": "M", "count": 9655, "year": 1880},
            {"name": "Mary", "gender": "F", "count": 1987, "year": 2020},
        ],
    )

    from src.query_helpers import query_by_year

    rows = query_by_year(db_path, 1880)

    assert rows == [
        {"name": "Mary", "gender": "F", "count": 7065, "year": 1880},
        {"name": "John", "gender": "M", "count": 9655, "year": 1880},
    ]


def test_query_helpers_returns_empty_list_when_no_match_exists(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    db_path = create_names_database(documents_dir)
    insert_name_records(
        db_path,
        [
            {"name": "Mary", "gender": "F", "count": 7065, "year": 1880},
        ],
    )

    from src.query_helpers import query_by_name

    rows = query_by_name(db_path, "Zelda")

    assert rows == []


def test_query_helpers_raises_for_unknown_column(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    db_path = create_names_database(documents_dir)

    from src.query_helpers import query_by_field

    try:
        query_by_field(db_path, "unknown_field", "Mary")
        raise AssertionError("Expected ValueError for unknown column")
    except ValueError as exc:
        assert "Unknown column" in str(exc)


def test_query_helpers_uses_read_only_database_access(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    db_path = create_names_database(documents_dir)
    insert_name_records(
        db_path,
        [
            {"name": "Mary", "gender": "F", "count": 7065, "year": 1880},
        ],
    )

    from src.query_helpers import query_by_name

    rows = query_by_name(db_path, "Mary")

    assert rows == [
        {"name": "Mary", "gender": "F", "count": 7065, "year": 1880},
    ]

    with sqlite3.connect(db_path) as connection:
        connection.execute("UPDATE names SET count = 999 WHERE name = 'Mary'")

    updated_rows = query_by_name(db_path, "Mary")

    assert updated_rows == [
        {"name": "Mary", "gender": "F", "count": 999, "year": 1880},
    ]
