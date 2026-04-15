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
    search_kwargs = {
        "query": query,
        "search_depth": "basic",
        "max_results": max_results,
        "include_answer": False,
        "time_range": f"d{days_back}",
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
        else:
            continue

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
