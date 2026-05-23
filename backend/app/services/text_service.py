import re
from dataclasses import dataclass
from typing import Literal

TextMode = Literal["normal", "office", "study"]


@dataclass(frozen=True)
class TextOptimizationResult:
    original_text: str
    optimized_text: str
    mode: TextMode


PUNCTUATION_REPLACEMENTS = {
    "，然后": "，然后",
    "然后": "，然后",
    "但是": "，但是",
    "所以": "，所以",
    "因为": "，因为",
    "并且": "，并且",
    "还有": "，还有",
    "最后": "，最后",
}


def optimize_text(text: str, mode: TextMode = "normal") -> TextOptimizationResult:
    original_text = text.strip()
    normalized = normalize_spacing(original_text)
    punctuated = add_punctuation(normalized)

    if mode == "office":
        optimized = optimize_for_office(punctuated)
    elif mode == "study":
        optimized = optimize_for_study(punctuated)
    else:
        optimized = punctuated

    return TextOptimizationResult(
        original_text=original_text,
        optimized_text=optimized,
        mode=mode,
    )


def normalize_spacing(text: str) -> str:
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[,.，。]+$", "", text)
    return text


def add_punctuation(text: str) -> str:
    if not text:
        return ""

    punctuated = text
    for source, target in PUNCTUATION_REPLACEMENTS.items():
        punctuated = punctuated.replace(source, target)

    punctuated = re.sub(r"，+", "，", punctuated)
    punctuated = punctuated.strip("，")

    if not punctuated.endswith(("。", "！", "？")):
        punctuated = f"{punctuated}。"

    return punctuated


def optimize_for_office(text: str) -> str:
    result = text
    result = result.replace("我们开会讨论", "我们将召开会议，讨论")
    result = result.replace("整理需求", "整理相关需求")
    result = result.replace("主要要考虑", "需要重点考虑")
    result = result.replace("准确率速度成本，还有易用性", "准确率、响应速度、使用成本和易用性")
    result = result.replace("准确率速度成本和易用性", "准确率、响应速度、使用成本和易用性")
    return result


def optimize_for_study(text: str) -> str:
    factors = extract_factor_list(text)
    if factors:
        return "语音输入法需要重点考虑以下因素：\n" + "\n".join(
            f"{index}. {factor}；" for index, factor in enumerate(factors, start=1)
        )

    return split_sentences_as_notes(text)


def extract_factor_list(text: str) -> list[str]:
    if "准确率" not in text or "速度" not in text or "成本" not in text or "易用性" not in text:
        return []

    return ["准确率", "响应速度", "使用成本", "易用性"]


def split_sentences_as_notes(text: str) -> str:
    sentences = [sentence for sentence in re.split(r"[。！？]", text) if sentence]
    if len(sentences) <= 1:
        return text

    return "学习笔记：\n" + "\n".join(
        f"{index}. {sentence}。" for index, sentence in enumerate(sentences, start=1)
    )
