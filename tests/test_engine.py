import os
from unittest.mock import patch, MagicMock
import pytest

from pulsescope.inference.engine import RiskEngine, InferenceError


@patch.dict(os.environ, {"OPENAI_API_KEY": "dummy"})
def test_engine_returns_risk_report():
    mock_completion = MagicMock()
    mock_completion.choices = [
        MagicMock(
            message=MagicMock(
                content='{"risk_level": "\u4e2d", "reasoning": "\u822a\u8fd0\u6210\u672c\u4e0a\u5347", "impact_chain": ["\u4e8b\u4ef61", "\u4e8b\u4ef62"], "suggested_metrics": ["BDI"]}'
            )
        )
    ]

    with patch("pulsescope.inference.engine.OpenAI") as MockOpenAI:
        instance = MockOpenAI.return_value
        instance.chat.completions.create.return_value = mock_completion
        engine = RiskEngine()
        report = engine.infer(company_name="\u4e07\u534e\u5316\u5b66", event={"\u4e8b\u4ef6": "\u4f0a\u6717\u5c01\u9501\u6d77\u5ce1", "\u7c7b\u578b": "\u5730\u7f18", "\u5f71\u54cd\u9886\u57df": "\u822a\u8fd0"})

    assert report["company"] == "\u4e07\u534e\u5316\u5b66"
    assert report["risk_level"] == "\u4e2d"
    assert "impact_chain" in report
    assert "suggested_metrics" in report


@patch.dict(os.environ, {"OPENAI_API_KEY": "dummy"})
def test_engine_strips_markdown_fences():
    mock_completion = MagicMock()
    mock_completion.choices = [
        MagicMock(
            message=MagicMock(
                content='Here is the report:\n```json\n{"risk_level": "\u9ad8", "reasoning": "X", "impact_chain": [], "suggested_metrics": []}\n```'
            )
        )
    ]

    with patch("pulsescope.inference.engine.OpenAI") as MockOpenAI:
        instance = MockOpenAI.return_value
        instance.chat.completions.create.return_value = mock_completion
        engine = RiskEngine()
        report = engine.infer(company_name="\u4e07\u534e\u5316\u5b66", event={"\u4e8b\u4ef6": "A", "\u7c7b\u578b": "B", "\u5f71\u54cd\u9886\u57df": "C"})

    assert report["risk_level"] == "\u9ad8"


@patch.dict(os.environ, {"OPENAI_API_KEY": "dummy"})
def test_engine_raises_on_invalid_json():
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="not json"))]

    with patch("pulsescope.inference.engine.OpenAI") as MockOpenAI:
        instance = MockOpenAI.return_value
        instance.chat.completions.create.return_value = mock_completion
        engine = RiskEngine()
        with pytest.raises(InferenceError):
            engine.infer(company_name="\u4e07\u534e\u5316\u5b66", event={"\u4e8b\u4ef6": "A", "\u7c7b\u578b": "B", "\u5f71\u54cd\u9886\u57df": "C"})


@patch.dict(os.environ, {}, clear=True)
def test_engine_raises_when_api_key_missing():
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY not set"):
        RiskEngine()
