from __future__ import annotations

import csv
from pathlib import Path


def _resolve_path(file_path: str | Path) -> Path:
    path = Path(file_path)
    candidates = [
        path,
        Path("documents") / path.name,
        Path("Documents") / path.name,
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return path


def list_yob_files(folder_path: str | Path) -> list[Path]:
    directory = Path(folder_path)

    if not directory.exists():
        return []

    return sorted(
        path for path in directory.iterdir()
        if path.is_file() and path.suffix == ".txt" and path.name.startswith("yob")
    )


def read_yob_file(file_path: str | Path) -> list[dict[str, str | int]]:
    resolved_path = _resolve_path(file_path)
    records: list[dict[str, str | int]] = []

    with resolved_path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)

        for row in reader:
            if not row or not any(cell.strip() for cell in row):
                continue

            if len(row) != 3:
                raise ValueError(
                    f"Expected 3 columns in {resolved_path}, got {len(row)}: {row}"
                )

            name, gender, count = (cell.strip() for cell in row)
            records.append({
                "name": name,
                "gender": gender,
                "count": int(count),
            })

    return records
