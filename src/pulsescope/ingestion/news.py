import os
from datetime import datetime, timedelta

from tavily import TavilyClient


def search_news(
    query: str,
    days_back: int = 7,
    max_results: int = 10,
    include_domains: list[str] | None = None,
) -> list[dict]:
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY not set")

    client = TavilyClient(api_key=api_key)
    # Tavily time_range expects day/week/month/year or d/w/m/y
    if days_back <= 1:
        time_range = "day"
    elif days_back <= 7:
        time_range = "week"
    elif days_back <= 30:
        time_range = "month"
    else:
        time_range = "year"

    search_kwargs = {
        "query": query,
        "search_depth": "basic",
        "max_results": max_results,
        "include_answer": False,
        "time_range": time_range,
    }
    if include_domains is not None:
        search_kwargs["include_domains"] = include_domains

    search_result = client.search(**search_kwargs)

    results = []
    cutoff = datetime.now() - timedelta(days=days_back)
    for item in search_result.get("results", []) or []:
        published = item.get("published_date") or item.get("date", "")
        if published:
            try:
                pub_dt = datetime.strptime(published[:10], "%Y-%m-%d")
            except ValueError:
                continue
            if pub_dt < cutoff:
                continue
        # If no date is present, trust Tavily's time_range filtering
        results.append(
            {
                "title": item.get("title", ""),
                "source": item.get("url", ""),
                "content": item.get("content", ""),
                "date": published[:10] if published else datetime.now().strftime("%Y-%m-%d"),
            }
        )

    return results
