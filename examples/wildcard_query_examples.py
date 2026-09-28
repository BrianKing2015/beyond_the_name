from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from src.etl import run_etl
from src.query_helpers import query_by_name, query_by_year


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

    for row in rows[:5]:
        print(row)


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    documents_dir = project_root / "Documents"
    db_path = ensure_database(documents_dir / "names.db")

    print(f"Using database: {db_path}")

    # Exact match: returns every record with that name in every year.
    print_rows("Exact match example", query_by_name(db_path, "Ava"))

    # Prefix wildcard: all names beginning with A.
    print_rows("Prefix wildcard example", query_by_name(db_path, "A%"))

    # Suffix wildcard: all names ending with a.
    print_rows("Suffix wildcard example", query_by_name(db_path, "%a"))

    # Year filter: all rows for the selected year.
    print_rows("Year filter example", query_by_year(db_path, 2023))

    print("\nTo try with your own values, edit the strings in this script and rerun it.")


if __name__ == "__main__":
    main()
