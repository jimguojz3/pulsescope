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
        {"company": "\u4e07\u534e\u5316\u5b66", "risk_level": "\u4e2d", "reasoning": "test"}
    ]
    result = analyze_company_risk(company_name="\u4e07\u534e\u5316\u5b66", days_back=7)
    assert "\u4e07\u534e\u5316\u5b66" in result
    assert "\u4e2d" in result


@patch("pulsescope.output.skill.analyze_company")
def test_analyze_company_risk_tool_returns_no_risk_when_empty(mock_analyze):
    mock_analyze.return_value = []
    result = analyze_company_risk(company_name="\u4e07\u534e\u5316\u5b66", days_back=7)
    assert "no_risk_events_detected" in result
