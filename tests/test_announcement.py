from datetime import datetime

from pulsescope.ingestion.announcement import fetch_announcements


FIXED_REF = datetime(2025, 4, 14)


def test_fetch_announcements_returns_filtered_records():
    results = fetch_announcements(
        company_name="万华化学",
        days_back=30,
        limit=10,
        reference_date=FIXED_REF,
    )
    assert len(results) == 3
    assert results[0]["date"] == "2025-04-10"
    assert results[1]["date"] == "2025-04-01"
    assert results[2]["date"] == "2025-03-20"


def test_fetch_announcements_respects_limit():
    results = fetch_announcements(
        company_name="万华化学",
        days_back=30,
        limit=2,
        reference_date=FIXED_REF,
    )
    assert len(results) == 2
    assert results[0]["date"] == "2025-04-10"
    assert results[1]["date"] == "2025-04-01"


def test_fetch_announcements_returns_empty_for_unknown_company():
    results = fetch_announcements(
        company_name="不存在的公司",
        days_back=30,
        limit=10,
        reference_date=FIXED_REF,
    )
    assert results == []


def test_fetch_announcements_skips_malformed_dates():
    results = fetch_announcements(
        company_name="中国石化",
        days_back=30,
        limit=10,
        reference_date=FIXED_REF,
    )
    assert len(results) == 1
    assert results[0]["title"] == "中国石化股份有限公司公告"
    assert results[0]["date"] == "2025-04-12"


def test_fetch_announcements_skips_out_of_range_dates():
    results = fetch_announcements(
        company_name="万华化学",
        days_back=10,
        limit=10,
        reference_date=FIXED_REF,
    )
    assert len(results) == 1
    assert results[0]["date"] == "2025-04-10"
