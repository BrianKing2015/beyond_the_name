from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from src.etl import run_etl
from src.query_helpers import query_name_timeline


def ensure_database(db_path: Path) -> Path:
    if not db_path.exists():
        print(f"Database not found at {db_path}. Loading data from Documents folder...")
        run_etl(db_path.parent)
    return db_path


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    documents_dir = project_root / "Documents"
    db_path = ensure_database(documents_dir / "names.db")

    print(f"Using database: {db_path}")

    for name in ["Mary", "John", "Olivia"]:
        timeline = query_name_timeline(db_path, name)
        print(f"\n{name}: {timeline}")

    print("\nTry changing the names above to explore a different timeline.")


if __name__ == "__main__":
    main()
