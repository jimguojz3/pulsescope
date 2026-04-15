"""Company announcement ingestion.

MVP uses a mock fallback so tests pass without external scraping dependencies.
In production this will be replaced with 巨潮资讯 / exchange crawlers.
"""

from datetime import datetime, timedelta


MOCK_DB = {
    "万华化学": [
        {
            "title": "万华化学 2025 年第一季度业绩公告",
            "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "content": "公司 MDI 产能达到 350 万吨/年，欧洲出口比例约 25%。",
        },
        {
            "title": "关于新增航线的公告",
            "date": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
            "content": "开通中东至欧洲直航航线，缩短航运周期 5 天。",
        },
    ],
    "中国石化": [
        {
            "title": "中国石化股份有限公司公告",
            "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "content": "原油进口合同续签，霍尔木兹航线为重要运输通道。",
        }
    ],
}


def fetch_announcements(company_name: str, days_back: int = 30, limit: int = 10) -> list[dict]:
    cutoff = datetime.now() - timedelta(days=days_back)
    records = MOCK_DB.get(company_name, [])
    results = []
    for r in records[:limit]:
        try:
            r_date = datetime.strptime(r["date"], "%Y-%m-%d")
        except ValueError:
            continue
        if r_date >= cutoff:
            results.append(r)
    return results
