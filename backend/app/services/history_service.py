from datetime import datetime

from app.services.json_store import read_json, write_json

HISTORY_FILE = "history.json"


def list_history() -> list[dict[str, object]]:
    records = read_json(HISTORY_FILE, [])
    if not isinstance(records, list):
        return []

    return sorted(
        [record for record in records if isinstance(record, dict)],
        key=lambda record: int(record.get("id", 0)),
        reverse=True,
    )


def save_history(text: str, mode: str) -> dict[str, object]:
    normalized = text.strip()
    if not normalized:
        raise ValueError("History text cannot be empty.")

    records = list(reversed(list_history()))
    next_id = max([int(record.get("id", 0)) for record in records], default=0) + 1
    record = {
        "id": next_id,
        "text": normalized,
        "mode": mode,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    records.append(record)
    write_json(HISTORY_FILE, records)
    return record
