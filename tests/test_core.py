from unittest.mock import patch, MagicMock

from pulsescope.core import analyze_company


def test_analyze_company_returns_report():
    mock_news = [
        {"title": "Test", "content": "Test news content", "source": "test", "date": "2025-04-10"}
    ]
    mock_announcements = [
        {"title": "Test Ann", "content": "Test announcement", "date": "2025-04-10", "source": "announcement"}
    ]
    mock_events = [
        {"事件": "测试事件", "类型": "测试", "影响领域": "航运"}
    ]
    mock_report = {
        "company": "万华化学",
        "event": "测试事件",
        "event_date": "",
        "risk_level": "低",
        "reasoning": "测试",
        "impact_chain": ["步骤1"],
        "suggested_metrics": ["测试指标"],
    }

    with patch("pulsescope.core.search_news", return_value=mock_news) as mock_search_news, \
         patch("pulsescope.core.fetch_announcements", return_value=mock_announcements) as mock_fetch_announcements, \
         patch("pulsescope.core.extract_events", return_value=mock_events) as mock_extract_events, \
         patch("pulsescope.core.RiskEngine") as MockRiskEngine:
        instance = MockRiskEngine.return_value
        instance.infer.return_value = mock_report
        reports = analyze_company(company_name="万华化学")

    assert isinstance(reports, list)
    assert len(reports) == 1
    assert reports[0]["company"] == "万华化学"
    assert reports[0]["risk_level"] == "低"
    mock_search_news.assert_called_once()
    mock_fetch_announcements.assert_called_once()
    mock_extract_events.assert_called_once()
    instance.infer.assert_called_once_with(company_name="万华化学", event=mock_events[0])


def test_analyze_company_returns_empty_when_no_texts():
    with patch("pulsescope.core.search_news", return_value=[]) as mock_search_news, \
         patch("pulsescope.core.fetch_announcements", return_value=[]) as mock_fetch_announcements, \
         patch("pulsescope.core.extract_events", return_value=[]) as mock_extract_events:
        reports = analyze_company(company_name="万华化学")

    assert reports == []
    mock_search_news.assert_called_once()
    mock_fetch_announcements.assert_called_once()
    mock_extract_events.assert_not_called()


def test_analyze_company_skips_unknown_risk_level():
    mock_news = [{"title": "Test", "content": "Test", "source": "test", "date": "2025-04-10"}]
    mock_events = [{"事件": "测试", "类型": "测试", "影响领域": "航运"}]
    mock_report_unknown = {
        "company": "万华化学",
        "event": "测试",
        "risk_level": "未知",
        "reasoning": "",
        "impact_chain": [],
        "suggested_metrics": [],
    }

    with patch("pulsescope.core.search_news", return_value=mock_news), \
         patch("pulsescope.core.fetch_announcements", return_value=[]), \
         patch("pulsescope.core.extract_events", return_value=mock_events), \
         patch("pulsescope.core.RiskEngine") as MockRiskEngine:
        instance = MockRiskEngine.return_value
        instance.infer.return_value = mock_report_unknown
        reports = analyze_company(company_name="万华化学")

    assert reports == []
