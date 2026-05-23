import json
from pathlib import Path
from typing import Any

STORAGE_DIR = Path(__file__).resolve().parents[1] / "storage"


def read_json(filename: str, default: Any) -> Any:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    path = STORAGE_DIR / filename
    if not path.exists():
        return default

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(filename: str, data: Any) -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    path = STORAGE_DIR / filename
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
