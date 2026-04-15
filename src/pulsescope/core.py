from typing import List

from pulsescope.extraction.extractor import extract_events
from pulsescope.ingestion.announcement import fetch_announcements
from pulsescope.ingestion.news import search_news
from pulsescope.inference.engine import RiskEngine


def analyze_company(company_name: str, days_back: int = 7) -> List[dict]:
    # 1. Fetch data
    news_items = search_news(query=company_name, days_back=days_back, max_results=5)
    announcements = fetch_announcements(company_name=company_name, days_back=days_back, limit=5)

    # 2. Build context for extraction
    texts = [n["content"] for n in news_items if n.get("content")]
    texts += [a["content"] for a in announcements if a.get("content")]

    # 3. Extract events
    events = extract_events(texts) if texts else []

    # 4. Infer risks
    reports = []
    if events:
        engine = RiskEngine()
        for evt in events:
            report = engine.infer(company_name=company_name, event=evt)
            if report.get("risk_level") != "\u672a\u77e5":
                reports.append(report)

    return reports
