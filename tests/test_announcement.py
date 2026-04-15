from pulsescope.ingestion.announcement import fetch_announcements


def test_fetch_announcements_returns_list():
    results = fetch_announcements(company_name="万华化学", days_back=30, limit=2)
    assert isinstance(results, list)
    if len(results) > 0:
        assert "title" in results[0]
        assert "date" in results[0]
        assert "content" in results[0]
