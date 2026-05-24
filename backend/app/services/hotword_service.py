import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any

from pypinyin import Style, lazy_pinyin

from app.services.json_store import read_json, write_json

HOTWORDS_FILE = "hotwords.json"


@dataclass(frozen=True)
class HotwordEntry:
    word: str
    aliases: list[str]

COMMON_CONFUSIONS = {
    "ASR": ["a s r", "A S R", "as r", "诶艾斯阿尔", "语音识别"],
    "Whisper": ["威士博", "威尔博", "维斯珀", "威斯珀", "whisper"],
    "FunASR": ["fun asr", "Fun ASR", "饭ASR", "方ASR"],
    "DeepSeek": ["deep seek", "Deep Seek", "迪普西克", "深度求索"],
    "SenseVoice": ["sense voice", "Sense Voice", "声音识别"],
}


def list_hotwords() -> list[dict[str, object]]:
    return [
        {"word": entry.word, "aliases": entry.aliases}
        for entry in read_hotword_entries()
    ]


def add_hotword(word: str, aliases: list[str] | None = None) -> dict[str, object]:
    normalized = word.strip()
    if not normalized:
        raise ValueError("Hotword cannot be empty.")

    normalized_aliases = normalize_aliases(aliases or [])
    entries = read_hotword_entries()
    updated_entries: list[HotwordEntry] = []
    found = False

    for entry in entries:
        if entry.word == normalized:
            found = True
            merged_aliases = normalize_aliases([*entry.aliases, *normalized_aliases])
            updated_entries.append(HotwordEntry(word=entry.word, aliases=merged_aliases))
        else:
            updated_entries.append(entry)

    if not found:
        updated_entries.append(HotwordEntry(word=normalized, aliases=normalized_aliases))

    write_hotword_entries(updated_entries)

    return {"word": normalized, "aliases": normalized_aliases}


def apply_hotword_corrections(text: str) -> str:
    corrected = text
    for entry in read_hotword_entries():
        hotword = entry.word
        candidates = build_candidates(entry)
        for candidate in candidates:
            if candidate and candidate != hotword:
                corrected = corrected.replace(candidate, hotword)
        corrected = correct_chinese_hotword_by_pinyin(corrected, hotword)
    return corrected


def build_candidates(entry: HotwordEntry) -> list[str]:
    hotword = entry.word
    candidates = COMMON_CONFUSIONS.get(hotword, [])
    return [
        *entry.aliases,
        *candidates,
        hotword.lower(),
        hotword.upper(),
        hotword.replace(" ", ""),
    ]


def read_hotword_entries() -> list[HotwordEntry]:
    raw_hotwords = read_json(HOTWORDS_FILE, [])
    if not isinstance(raw_hotwords, list):
        return []

    entries: list[HotwordEntry] = []
    for item in raw_hotwords:
        entry = parse_hotword_entry(item)
        if entry:
            entries.append(entry)

    return entries


def parse_hotword_entry(item: Any) -> HotwordEntry | None:
    if isinstance(item, str):
        word = item.strip()
        return HotwordEntry(word=word, aliases=[]) if word else None

    if isinstance(item, dict):
        word = str(item.get("word", "")).strip()
        aliases = item.get("aliases", [])
        if not word:
            return None
        if not isinstance(aliases, list):
            aliases = []
        return HotwordEntry(word=word, aliases=normalize_aliases(aliases))

    return None


def write_hotword_entries(entries: list[HotwordEntry]) -> None:
    write_json(
        HOTWORDS_FILE,
        [{"word": entry.word, "aliases": entry.aliases} for entry in entries],
    )


def normalize_aliases(aliases: list[str]) -> list[str]:
    normalized_aliases: list[str] = []
    for alias in aliases:
        normalized = alias.strip()
        if normalized and normalized not in normalized_aliases:
            normalized_aliases.append(normalized)
    return normalized_aliases


def correct_chinese_hotword_by_pinyin(text: str, hotword: str) -> str:
    if not hotword or not is_chinese_text(hotword):
        return text

    hotword_length = len(hotword)
    if hotword_length < 2:
        return text

    hotword_pinyin = pinyin_signature(hotword)
    corrected = text

    candidates = {
        text[index : index + hotword_length]
        for index in range(0, max(len(text) - hotword_length + 1, 0))
        if is_chinese_text(text[index : index + hotword_length])
    }

    for candidate in candidates:
        if candidate == hotword:
            continue

        if pinyin_similarity(candidate, hotword_pinyin) >= 0.92:
            corrected = corrected.replace(candidate, hotword)

    return corrected


def is_chinese_text(text: str) -> bool:
    return bool(re.fullmatch(r"[\u4e00-\u9fff]+", text))


def pinyin_signature(text: str) -> str:
    return " ".join(lazy_pinyin(text, style=Style.NORMAL))


def pinyin_similarity(candidate: str, hotword_pinyin: str) -> float:
    candidate_pinyin = pinyin_signature(candidate)
    return SequenceMatcher(None, candidate_pinyin, hotword_pinyin).ratio()
