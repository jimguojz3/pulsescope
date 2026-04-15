import os
from datetime import datetime, timedelta

from tavily import TavilyClient


def search_news(query: str, days_back: int = 7, max_results: int = 10) -> list[dict]:
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY not set")

    client = TavilyClient(api_key=api_key)
    search_result = client.search(
        query=query,
        search_depth="basic",
        max_results=max_results,
        include_answer=False,
    )

    results = []
    cutoff = datetime.now() - timedelta(days=days_back)
    for item in getattr(search_result, "results", []) or []:
        published = item.get("published_date") or item.get("date", "")
        if published:
            try:
                pub_dt = datetime.strptime(published[:10], "%Y-%m-%d")
            except ValueError:
                pub_dt = datetime.now()
        else:
            pub_dt = datetime.now()

        if pub_dt >= cutoff:
            results.append(
                {
                    "title": item.get("title", ""),
                    "source": item.get("url", ""),
                    "content": item.get("content", ""),
                    "date": published[:10] if published else datetime.now().strftime("%Y-%m-%d"),
                }
            )

    return results
