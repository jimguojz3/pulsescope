import json
import logging
import os
import re
from typing import List

from openai import OpenAI

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """你是一个专业的供应链风险事件抽取助手。请从下面的新闻文本中，抽取出对化工、大宗商品、航运企业可能产生风险的关键事件。
请以 JSON 数组格式输出，每个事件包含以下字段：
- 事件: 事件的简短描述
- 类型: 地缘政治 / 自然灾害 / 政策监管 / 市场价格 / 运营异常
- 影响领域: 航运 / 能源 / 原材料 / 市场需求 / 政策
如果没有风险事件，返回空数组 []。"""


class ExtractionError(Exception):
    """Raised when event extraction fails due to unparseable model output."""
    pass


def _strip_markdown_fences(text: str) -> str:
    """Remove markdown JSON code fences and any preceding explanatory text."""
    # Match everything after the last opening fence ```json or ```
    pattern = r"```(?:json)?\s*([\s\S]*?)```\s*$"
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    # No fences found — just strip whitespace
    return text.strip()


def extract_events(texts: List[str]) -> List[dict]:
    """Extract risk events from a list of texts using an LLM.

    Args:
        texts: List of news/announcement strings to analyze.

    Returns:
        List of event dictionaries. Empty list if no events are found.

    Raises:
        RuntimeError: If OPENAI_API_KEY is not set.
        ExtractionError: If the model returns output that cannot be parsed as a JSON list.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    client = OpenAI(api_key=api_key, base_url=base_url)
    combined = "\n\n".join(f"[{i+1}] {t}" for i, t in enumerate(texts))

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": combined},
        ],
        temperature=0.2,
    )

    raw = response.choices[0].message.content or "[]"
    content = _strip_markdown_fences(raw)

    try:
        events = json.loads(content)
    except json.JSONDecodeError as exc:
        logger.warning("Failed to parse LLM output as JSON: %s", exc)
        raise ExtractionError(f"Invalid JSON from model: {exc}") from exc

    if not isinstance(events, list):
        raise ExtractionError(f"Expected JSON list, got {type(events).__name__}")

    return events
