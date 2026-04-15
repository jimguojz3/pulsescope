import json
import os
from typing import List

from openai import OpenAI


_SYSTEM_PROMPT = """你是一个专业的供应链风险事件抽取助手。请从下面的新闻文本中，抽取出对化工、大宗商品、航运企业可能产生风险的关键事件。
请以 JSON 数组格式输出，每个事件包含以下字段：
- 事件: 事件的简短描述
- 类型: 地缘政治 / 自然灾害 / 政策监管 / 市场价格 / 运营异常
- 影响领域: 航运 / 能源 / 原材料 / 市场需求 / 政策
如果没有风险事件，返回空数组 []。"""


def extract_events(texts: List[str]) -> List[dict]:
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    client = OpenAI(api_key=api_key, base_url=base_url)
    combined = "\n\n".join(f"[{i+1}] {t}" for i, t in enumerate(texts))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": combined},
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content or "[]"
    # Strip markdown code fences if present
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    try:
        events = json.loads(content)
    except json.JSONDecodeError:
        events = []

    if not isinstance(events, list):
        events = []

    return events
