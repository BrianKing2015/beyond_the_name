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


def test_query_helpers_supports_wildcard_name_matches(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    db_path = create_names_database(documents_dir)
    insert_name_records(
        db_path,
        [
            {"name": "Mary", "gender": "F", "count": 7065, "year": 1880},
            {"name": "Martha", "gender": "F", "count": 5432, "year": 1880},
            {"name": "John", "gender": "M", "count": 9655, "year": 1880},
            {"name": "Mary", "gender": "F", "count": 1987, "year": 2020},
            {"name": "Rory", "gender": "M", "count": 1200, "year": 2020},
        ],
    )

    from src.query_helpers import query_by_name

    prefix_rows = query_by_name(db_path, "Mar%")
    assert prefix_rows == [
        {"name": "Mary", "gender": "F", "count": 7065, "year": 1880},
        {"name": "Martha", "gender": "F", "count": 5432, "year": 1880},
        {"name": "Mary", "gender": "F", "count": 1987, "year": 2020},
    ]

    suffix_rows = query_by_name(db_path, "%ry")
    assert suffix_rows == [
        {"name": "Mary", "gender": "F", "count": 7065, "year": 1880},
        {"name": "Mary", "gender": "F", "count": 1987, "year": 2020},
        {"name": "Rory", "gender": "M", "count": 1200, "year": 2020},
    ]


def test_query_helpers_returns_top_names_for_year(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    db_path = create_names_database(documents_dir)
    insert_name_records(
        db_path,
        [
            {"name": "Mary", "gender": "F", "count": 7065, "year": 1880},
            {"name": "John", "gender": "M", "count": 9655, "year": 1880},
            {"name": "Jane", "gender": "F", "count": 7888, "year": 1880},
            {"name": "Mary", "gender": "F", "count": 1987, "year": 2020},
            {"name": "John", "gender": "M", "count": 9100, "year": 2020},
        ],
    )

    from src.query_helpers import query_top_names_by_year

    rows = query_top_names_by_year(db_path, 1880, limit=2)

    assert rows == [
        {"name": "John", "gender": "M", "count": 9655, "year": 1880},
        {"name": "Jane", "gender": "F", "count": 7888, "year": 1880},
    ]

    female_rows = query_top_names_by_year(db_path, 1880, limit=2, gender="F")

    assert female_rows == [
        {"name": "Jane", "gender": "F", "count": 7888, "year": 1880},
        {"name": "Mary", "gender": "F", "count": 7065, "year": 1880},
    ]


def test_query_helpers_returns_first_and_peak_year_for_name(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    db_path = create_names_database(documents_dir)
    insert_name_records(
        db_path,
        [
            {"name": "Mary", "gender": "F", "count": 7065, "year": 1880},
            {"name": "Mary", "gender": "F", "count": 9200, "year": 1881},
            {"name": "Mary", "gender": "F", "count": 9000, "year": 1882},
            {"name": "John", "gender": "M", "count": 9655, "year": 1880},
            {"name": "John", "gender": "M", "count": 9400, "year": 1881},
        ],
    )

    from src.query_helpers import query_name_timeline

    result = query_name_timeline(db_path, "Mary")

    assert result == {
        "name": "Mary",
        "first_year": 1880,
        "peak_year": 1881,
        "peak_count": 9200,
    }


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
