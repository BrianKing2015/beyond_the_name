from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from src.etl import run_etl
from src.query_helpers import query_top_names_by_year


def ensure_database(db_path: Path) -> Path:
    if not db_path.exists():
        print(f"Database not found at {db_path}. Loading data from Documents folder...")
        run_etl(db_path.parent)
    return db_path


def print_rows(label: str, rows: list[dict[str, object]]) -> None:
    print(f"\n{label}: {len(rows)} row(s)")
    if not rows:
        print("No matches.")
        return

    for row in rows:
        print(row)


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    documents_dir = project_root / "Documents"
    db_path = ensure_database(documents_dir / "names.db")

    print(f"Using database: {db_path}")

    # Top 5 names in a year, regardless of gender.
    print_rows("Top 5 names in 2023", query_top_names_by_year(db_path, 2023, limit=5))

    # Top 3 female names in a given year.
    print_rows("Top 3 female names in 2023", query_top_names_by_year(db_path, 2023, limit=3, gender="F"))

    # Top 10 names in a different year.
    print_rows("Top 10 names in 1880", query_top_names_by_year(db_path, 1880, limit=10))

    print("\nAdjust the year, limit, and gender to explore different views of the data.")


if __name__ == "__main__":
    main()
