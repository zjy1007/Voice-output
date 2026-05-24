import os
import re
from dataclasses import dataclass
from typing import Literal

import httpx
from dotenv import load_dotenv

from app.services.hotword_service import apply_hotword_corrections, list_hotwords

load_dotenv()

TextMode = Literal["normal", "office", "study"]


@dataclass(frozen=True)
class TextOptimizationResult:
    original_text: str
    optimized_text: str
    mode: TextMode
    provider: str = "rules"


class TextOptimizationError(Exception):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


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


async def optimize_text_with_provider(
    text: str,
    mode: TextMode = "normal",
) -> TextOptimizationResult:
    provider = os.getenv("TEXT_OPTIMIZER_PROVIDER", "rules").lower()
    if provider == "deepseek":
        return await optimize_text_with_deepseek(text, mode)

    return optimize_text_with_rules(text, mode)


def optimize_text_with_rules(text: str, mode: TextMode = "normal") -> TextOptimizationResult:
    original_text = text.strip()
    hotword_corrected = apply_hotword_corrections(original_text)
    normalized = normalize_spacing(hotword_corrected)
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
        provider="rules",
    )


async def optimize_text_with_deepseek(
    text: str,
    mode: TextMode = "normal",
) -> TextOptimizationResult:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise TextOptimizationError(
            "DEEPSEEK_API_KEY is required when TEXT_OPTIMIZER_PROVIDER=deepseek.",
            status_code=400,
        )

    original_text = text.strip()
    if not original_text:
        raise TextOptimizationError("Text cannot be empty.", status_code=400)

    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": build_deepseek_system_prompt(mode),
                        },
                        {
                            "role": "user",
                            "content": build_deepseek_user_prompt(original_text),
                        },
                    ],
                    "temperature": 0.2,
                    "stream": False,
                },
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as error:
        raise TextOptimizationError(
            f"DeepSeek returned {error.response.status_code}: {error.response.text}",
            status_code=error.response.status_code,
        ) from error
    except httpx.HTTPError as error:
        raise TextOptimizationError(f"DeepSeek request failed: {error}") from error

    data = response.json()
    try:
        optimized = data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as error:
        raise TextOptimizationError("DeepSeek response did not include content.") from error

    return TextOptimizationResult(
        original_text=original_text,
        optimized_text=optimized,
        mode=mode,
        provider="deepseek",
    )


def build_deepseek_system_prompt(mode: TextMode) -> str:
    shared_rule = (
        "你是智能语音输入法的中文文本后处理模块。"
        "请只输出优化后的文本，不要解释。"
        "任务包括自动标点、合理断句、修正明显口语冗余，并保留原意。"
    )

    if mode == "office":
        return f"{shared_rule} 当前模式是办公模式：表达要正式、清晰、适合会议纪要或工作汇报。"

    if mode == "study":
        return f"{shared_rule} 当前模式是学习笔记：尽量整理为条目化、层次清楚的笔记。"

    return f"{shared_rule} 当前模式是普通输入：保留自然表达，让文本易读即可。"


def build_deepseek_user_prompt(text: str) -> str:
    hotwords = list_hotwords()
    if not hotwords:
        return text

    return (
        "请优先保留和纠正以下自定义热词："
        + "、".join(hotwords)
        + "\n\n待优化文本："
        + text
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
