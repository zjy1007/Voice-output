from app.services.json_store import read_json, write_json

HOTWORDS_FILE = "hotwords.json"


def list_hotwords() -> list[str]:
    hotwords = read_json(HOTWORDS_FILE, [])
    return [word for word in hotwords if isinstance(word, str)]


def add_hotword(word: str) -> str:
    normalized = word.strip()
    if not normalized:
        raise ValueError("Hotword cannot be empty.")

    hotwords = list_hotwords()
    if normalized not in hotwords:
        hotwords.append(normalized)
        write_json(HOTWORDS_FILE, hotwords)

    return normalized
