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

    # Exact name query: returns every record for a given name across years.
    print_rows("Exact name lookup", query_by_name(db_path, "Mary"))

    # Exact year query: returns every record in that year.
    print_rows("Exact year lookup", query_by_year(db_path, 2020))

    # A second exact-name example shows how easy it is to swap values.
    print_rows("Another exact name lookup", query_by_name(db_path, "John"))

    print("\nUse these examples as a starting point for your own searches.")


if __name__ == "__main__":
    main()
