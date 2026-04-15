import os
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from pulsescope.ingestion.news import search_news


@patch.dict(os.environ, {"TAVILY_API_KEY": "fake-key"})
@patch("pulsescope.ingestion.news.datetime")
def test_search_news_returns_list(mock_datetime):
    mock_datetime.now.return_value = datetime(2025, 4, 15)
    mock_datetime.strptime = datetime.strptime
    mock_datetime.timedelta = timedelta

    search_result = {
        "results": [
            {
                "title": "Iran blocks Strait of Hormuz",
                "url": "https://example.com/1",
                "content": "Iran has closed the Strait of Hormuz to shipping.",
                "published_date": "2025-04-10",
            }
        ]
    }

    with patch("pulsescope.ingestion.news.TavilyClient") as MockClient:
        instance = MockClient.return_value
        instance.search.return_value = search_result
        results = search_news(query="Iran Strait Hormuz", days_back=7, max_results=5)

    assert len(results) == 1
    assert results[0]["title"] == "Iran blocks Strait of Hormuz"
    assert "source" in results[0]
    assert "date" in results[0]


def test_search_news_raises_without_api_key():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="TAVILY_API_KEY not set"):
            search_news(query="test")


@patch.dict(os.environ, {"TAVILY_API_KEY": "fake-key"})
@patch("pulsescope.ingestion.news.datetime")
def test_search_news_skips_missing_dates(mock_datetime):
    mock_datetime.now.return_value = datetime(2025, 4, 15)
    mock_datetime.strptime = datetime.strptime
    mock_datetime.timedelta = timedelta

    search_result = {
        "results": [
            {
                "title": "Article with no date",
                "url": "https://example.com/no-date",
                "content": "This article has no date field.",
            }
        ]
    }

    with patch("pulsescope.ingestion.news.TavilyClient") as MockClient:
        instance = MockClient.return_value
        instance.search.return_value = search_result
        results = search_news(query="test", days_back=7)

    assert len(results) == 0


@patch.dict(os.environ, {"TAVILY_API_KEY": "fake-key"})
@patch("pulsescope.ingestion.news.datetime")
def test_search_news_skips_malformed_dates(mock_datetime):
    mock_datetime.now.return_value = datetime(2025, 4, 15)
    mock_datetime.strptime = datetime.strptime
    mock_datetime.timedelta = timedelta

    search_result = {
        "results": [
            {
                "title": "Article with bad date",
                "url": "https://example.com/bad-date",
                "content": "This article has a malformed date.",
                "published_date": "not-a-date",
            }
        ]
    }

    with patch("pulsescope.ingestion.news.TavilyClient") as MockClient:
        instance = MockClient.return_value
        instance.search.return_value = search_result
        results = search_news(query="test", days_back=7)

    assert len(results) == 0


@patch.dict(os.environ, {"TAVILY_API_KEY": "fake-key"})
@patch("pulsescope.ingestion.news.datetime")
def test_search_news_skips_out_of_range_dates(mock_datetime):
    mock_datetime.now.return_value = datetime(2025, 4, 15)
    mock_datetime.strptime = datetime.strptime
    mock_datetime.timedelta = timedelta

    search_result = {
        "results": [
            {
                "title": "Old article",
                "url": "https://example.com/old",
                "content": "This article is too old.",
                "published_date": "2025-04-01",
            }
        ]
    }

    with patch("pulsescope.ingestion.news.TavilyClient") as MockClient:
        instance = MockClient.return_value
        instance.search.return_value = search_result
        results = search_news(query="test", days_back=7)

    assert len(results) == 0
