from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from src.csv_reader import list_yob_files, read_yob_file
from src.sqlite_loader import create_names_database, insert_name_records


def run_etl(documents_dir: str | Path) -> Path:
    directory = Path(documents_dir)
    db_path = create_names_database(directory)

    records: list[dict[str, object]] = []
    for yob_file in list_yob_files(directory):
        year = int(yob_file.stem.replace("yob", ""))
        for row in read_yob_file(yob_file):
            row_with_year: dict[str, object] = {
                "name": row["name"],
                "gender": row["gender"],
                "count": row["count"],
                "year": year,
            }
            records.append(row_with_year)

    insert_name_records(db_path, records)
    return db_path


if __name__ == "__main__":
    documents_dir = Path(__file__).resolve().parent.parent / "Documents"
    db_path = run_etl(documents_dir)
    print(f"Loaded yob data into {db_path}")
