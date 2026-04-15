import asyncio
from unittest.mock import patch

from pulsescope.output.skill import analyze_company_risk, mcp_app


def test_skill_exposes_analyze_tool():
    tools = asyncio.run(mcp_app.list_tools())
    names = [t.name for t in tools]
    assert "analyze_company_risk" in names


@patch("pulsescope.output.skill.analyze_company")
def test_analyze_company_risk_tool_returns_json(mock_analyze):
    mock_analyze.return_value = [
        {"company": "万华化学", "risk_level": "中", "reasoning": "test"}
    ]
    result = analyze_company_risk(company_name="万华化学", days_back=7)
    assert "万华化学" in result
    assert "中" in result


@patch("pulsescope.output.skill.analyze_company")
def test_analyze_company_risk_tool_returns_no_risk_when_empty(mock_analyze):
    mock_analyze.return_value = []
    result = analyze_company_risk(company_name="万华化学", days_back=7)
    assert "no_risk_events_detected" in result


def test_analyze_company_risk_tool_returns_error_for_invalid_days_back():
    result = analyze_company_risk(company_name="万华化学", days_back=0)
    data = __import__("json").loads(result)
    assert data["status"] == "error"
    assert "days_back" in data["message"]


@patch("pulsescope.output.skill.analyze_company")
def test_analyze_company_risk_tool_returns_error_on_exception(mock_analyze):
    mock_analyze.side_effect = RuntimeError("pipeline failed")
    result = analyze_company_risk(company_name="万华化学", days_back=7)
    data = __import__("json").loads(result)
    assert data["status"] == "error"
    assert "pipeline failed" in data["message"]
