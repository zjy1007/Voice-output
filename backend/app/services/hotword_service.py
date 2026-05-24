import re
from difflib import SequenceMatcher

from pypinyin import Style, lazy_pinyin

from app.services.json_store import read_json, write_json

HOTWORDS_FILE = "hotwords.json"

COMMON_CONFUSIONS = {
    "ASR": ["a s r", "A S R", "as r", "诶艾斯阿尔", "语音识别"],
    "Whisper": ["威士博", "威尔博", "维斯珀", "威斯珀", "whisper"],
    "FunASR": ["fun asr", "Fun ASR", "饭ASR", "方ASR"],
    "DeepSeek": ["deep seek", "Deep Seek", "迪普西克", "深度求索"],
    "SenseVoice": ["sense voice", "Sense Voice", "声音识别"],
}


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


def apply_hotword_corrections(text: str) -> str:
    corrected = text
    for hotword in list_hotwords():
        candidates = build_candidates(hotword)
        for candidate in candidates:
            if candidate and candidate != hotword:
                corrected = corrected.replace(candidate, hotword)
        corrected = correct_chinese_hotword_by_pinyin(corrected, hotword)
    return corrected


def build_candidates(hotword: str) -> list[str]:
    candidates = COMMON_CONFUSIONS.get(hotword, [])
    return [
        *candidates,
        hotword.lower(),
        hotword.upper(),
        hotword.replace(" ", ""),
    ]


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
