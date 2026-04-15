import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from pulsescope.ingestion.news import search_news


@patch.dict(os.environ, {"TAVILY_API_KEY": "fake-key"})
@patch("pulsescope.ingestion.news.datetime")
def test_search_news_returns_list(mock_datetime):
    mock_datetime.now.return_value = datetime(2025, 4, 15)
    mock_datetime.strptime = datetime.strptime
    mock_datetime.timedelta = timedelta

    mock_response = MagicMock()
    mock_response.results = [
        {
            "title": "Iran blocks Strait of Hormuz",
            "url": "https://example.com/1",
            "content": "Iran has closed the Strait of Hormuz to shipping.",
            "published_date": "2025-04-10",
        }
    ]

    with patch("pulsescope.ingestion.news.TavilyClient") as MockClient:
        instance = MockClient.return_value
        instance.search.return_value = mock_response
        results = search_news(query="Iran Strait Hormuz", days_back=7, max_results=5)

    assert len(results) == 1
    assert results[0]["title"] == "Iran blocks Strait of Hormuz"
    assert "source" in results[0]
    assert "date" in results[0]
