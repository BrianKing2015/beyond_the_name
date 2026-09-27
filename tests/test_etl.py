import sqlite3

from src.etl import run_etl


def test_etl_runs_for_all_yob_files(tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    (documents_dir / "yob1880.txt").write_text(
        "Mary,F,7065\nJohn,M,9655\n",
        encoding="utf-8",
    )
    (documents_dir / "yob1881.txt").write_text(
        "Mary,F,1987\nEmma,F,1234\n",
        encoding="utf-8",
    )

    db_path = run_etl(documents_dir)

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT name, gender, count, year FROM names ORDER BY year, id"
        ).fetchall()

    assert rows == [
        ("Mary", "F", 7065, 1880),
        ("John", "M", 9655, 1880),
        ("Mary", "F", 1987, 1881),
        ("Emma", "F", 1234, 1881),
    ]
