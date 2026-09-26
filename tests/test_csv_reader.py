from pathlib import Path

from src.csv_reader import list_yob_files, read_yob_file


def test_yob_reader_reads_rows_from_documents_folder(tmp_path):
    file_path = tmp_path / "yob1880.txt"
    file_path.write_text("Mary,F,7065\nJohn,M,9655\n", encoding="utf-8")

    records = read_yob_file(file_path)

    assert len(records) > 0


def test_yob_reader_lists_yob_files_in_directory(tmp_path):
    (tmp_path / "yob1880.txt").write_text("Mary,F,7065\n", encoding="utf-8")
    (tmp_path / "yob1881.txt").write_text("John,M,9655\n", encoding="utf-8")

    files = list_yob_files(tmp_path)

    assert len(files) > 1


def test_yob_reader_normalizes_data_types(tmp_path):
    file_path = tmp_path / "yob1880.txt"
    file_path.write_text("Mary,F,7065\n", encoding="utf-8")

    records = read_yob_file(file_path)
    first_record = records[0]

    assert set(first_record.keys()) == {"name", "gender", "count"}
    assert isinstance(first_record["name"], str)
    assert isinstance(first_record["gender"], str)
    assert isinstance(first_record["count"], int)


def test_yob_reader_filters_only_yob_files_and_reads_every_file(tmp_path):
    (tmp_path / "notes.txt").write_text("not a name file\n", encoding="utf-8")
    (tmp_path / "yob1880.txt").write_text("Mary,F,7065\nJohn,M,9655\n", encoding="utf-8")
    (tmp_path / "yob1881.txt").write_text("Emma,F,2003\nJames,M,8746\n", encoding="utf-8")

    files = list_yob_files(tmp_path)

    assert [path.name for path in files] == ["yob1880.txt", "yob1881.txt"]

    for file_path in files:
        records = read_yob_file(file_path)
        assert len(records) > 0


def test_yob_reader_normalizes_values(tmp_path):
    file_path = tmp_path / "yob1880.txt"
    file_path.write_text("Mary,F,7065\n", encoding="utf-8")

    records = read_yob_file(file_path)
    first_record = records[0]

    assert first_record == {
        "name": "Mary",
        "gender": "F",
        "count": 7065,
    }


def test_yob_reader_raises_clear_error_when_yob_file_is_missing(tmp_path):
    missing_file = tmp_path / "missing_yob_file.txt"

    try:
        read_yob_file(missing_file)
        assert False, "Expected FileNotFoundError to be raised"
    except FileNotFoundError:
        pass


def test_yob_reader_skips_blank_rows(tmp_path):
    file_path = tmp_path / "yob1880.txt"
    file_path.write_text("\nMary,F,7065\n\nJohn,M,9655\n\n", encoding="utf-8")

    records = read_yob_file(file_path)

    assert [row["name"] for row in records] == ["Mary", "John"]


def test_yob_reader_handles_invalid_row_shapes(tmp_path):
    file_path = tmp_path / "yob1880.txt"
    file_path.write_text("Mary,F,7065\nBadRow\n", encoding="utf-8")

    try:
        read_yob_file(file_path)
        assert False, "Expected ValueError to be raised"
    except ValueError:
        pass
