import json
import logging
import os
import re

from openai import OpenAI

from pulsescope.knowledge.graph import KnowledgeGraph
from pulsescope.knowledge.seeds import load_seed_companies

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """你是供应链风险推理专家。根据以下企业背景、关键事件和产业链信息，输出一份结构化风险报告。

请严格按以下 JSON 格式输出（不要有 markdown 标记）：
{
  "risk_level": "高" | "中" | "低",
  "reasoning": "用 1-2 句话解释风险定级的原因",
  "impact_chain": ["步骤1", "步骤2", "步骤3"],
  "suggested_metrics": ["关注指标1", "关注指标2"]
}
"""


class InferenceError(Exception):
    """Raised when risk inference fails due to unparseable model output."""
    pass


def _strip_markdown_fences(text: str) -> str:
    """Remove markdown JSON code fences and any preceding explanatory text."""
    pattern = r"```(?:json)?\s*([\s\S]*?)```\s*$"
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return text.strip()


class RiskEngine:
    def __init__(self):
        self._kg = KnowledgeGraph()
        self._kg.load_from_seed(load_seed_companies())
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self._model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self._client = OpenAI(api_key=api_key, base_url=base_url)

    def infer(self, company_name: str, event: dict) -> dict:
        routes = self._kg.query_routes(company_name)
        company_node = next(
            (n for n in self._kg._g.nodes if n == company_name), None
        )
        products = []
        materials = []
        if company_node:
            for neighbor in self._kg._g.neighbors(company_node):
                rel = self._kg._g.edges[company_node, neighbor].get("relation")
                if rel == "produces":
                    products.append(neighbor)
                elif rel == "uses":
                    materials.append(neighbor)

        context = f"""企业: {company_name}
产品: {', '.join(products) or '未知'}
原材料: {', '.join(materials) or '未知'}
航线: {', '.join(routes) or '未知'}
事件: {event.get('事件', '')}
类型: {event.get('类型', '')}
影响领域: {event.get('影响领域', '')}
"""

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": context},
            ],
            temperature=0.2,
        )

        raw = response.choices[0].message.content or "{}"
        content = _strip_markdown_fences(raw)

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            logger.warning("Failed to parse LLM output as JSON: %s", exc)
            raise InferenceError(f"Invalid JSON from model: {exc}") from exc

        if not isinstance(parsed, dict):
            raise InferenceError(f"Expected JSON object, got {type(parsed).__name__}")

        report = {
            "company": company_name,
            "event": event.get("事件", ""),
            "event_date": event.get("日期", ""),
            "risk_level": parsed.get("risk_level", "未知"),
            "reasoning": parsed.get("reasoning", ""),
            "impact_chain": parsed.get("impact_chain", []),
            "suggested_metrics": parsed.get("suggested_metrics", []),
        }
        return report
