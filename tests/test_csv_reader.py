from pathlib import Path

from src.csv_reader import list_name_files, read_name_file


def test_read_first_yob_file_returns_non_zero_list():
    file_path = Path("documents") / "yob1880.txt"

    records = read_name_file(file_path)

    assert len(records) > 0


def test_list_name_files_returns_more_than_one_file():
    files = list_name_files("documents")

    assert len(files) > 1


def test_read_name_file_returns_expected_schema():
    records = read_name_file(Path("documents") / "yob1880.txt")

    first_record = records[0]

    assert set(first_record.keys()) == {"name", "gender", "count"}
    assert isinstance(first_record["name"], str)
    assert isinstance(first_record["gender"], str)
    assert isinstance(first_record["count"], int)


def test_list_name_files_only_includes_yob_pattern_and_reads_every_file(tmp_path):
    (tmp_path / "notes.txt").write_text("not a name file\n", encoding="utf-8")
    (tmp_path / "yob1880.txt").write_text("Mary,F,7065\nJohn,M,9655\n", encoding="utf-8")
    (tmp_path / "yob1881.txt").write_text("Emma,F,2003\nJames,M,8746\n", encoding="utf-8")

    files = list_name_files(tmp_path)

    assert [path.name for path in files] == ["yob1880.txt", "yob1881.txt"]

    for file_path in files:
        records = read_name_file(file_path)
        assert len(records) > 0


def test_read_name_file_normalizes_field_names_and_values():
    records = read_name_file(Path("documents") / "yob1880.txt")

    first_record = records[0]

    assert first_record == {
        "name": "Mary",
        "gender": "F",
        "count": 7065,
    }


def test_read_name_file_raises_for_missing_file():
    missing_file = Path("documents") / "missing_yob_file.txt"

    try:
        read_name_file(missing_file)
        assert False, "Expected FileNotFoundError to be raised"
    except FileNotFoundError:
        pass
