"""Company announcement ingestion.

MVP uses a mock fallback so tests pass without external scraping dependencies.
In production this will be replaced with 巨潮资讯 / exchange crawlers.
"""

from datetime import datetime, timedelta


MOCK_DB = {
    "万华化学": [
        {
            "title": "万华化学 2025 年第一季度业绩公告",
            "date": "2025-04-10",
            "content": "公司 MDI 产能达到 350 万吨/年，欧洲出口比例约 25%。",
        },
        {
            "title": "关于新增航线的公告",
            "date": "2025-04-01",
            "content": "开通中东至欧洲直航航线，缩短航运周期 5 天。",
        },
        {
            "title": "万华化学 2024 年度年度报告",
            "date": "2025-03-20",
            "content": "年度营收同比增长 8%。",
        },
        {
            "title": "历史公告",
            "date": "2024-12-01",
            "content": "早期公告内容。",
        },
    ],
    "中国石化": [
        {
            "title": "中国石化股份有限公司公告",
            "date": "2025-04-12",
            "content": "原油进口合同续签，霍尔木兹航线为重要运输通道。",
        },
        {
            "title": " malformed date record ",
            "date": "not-a-date",
            "content": "This record has a bad date string.",
        },
        {
            "title": "旧公告",
            "date": "2024-01-15",
            "content": "过期内容。",
        },
    ],
    "TestCorp": [
        {
            "title": "Edge case on cutoff",
            "date": "2025-03-15",
            "content": "Exactly 30 days before reference.",
        },
    ],
}


def fetch_announcements(
    company_name: str,
    days_back: int = 30,
    limit: int = 10,
    reference_date: datetime | None = None,
) -> list[dict]:
    ref = reference_date if reference_date is not None else datetime.now()
    cutoff = ref - timedelta(days=days_back)
    records = MOCK_DB.get(company_name, [])
    results = []
    for r in records:
        try:
            r_date = datetime.strptime(r["date"], "%Y-%m-%d")
        except ValueError:
            continue
        if r_date >= cutoff:
            results.append(r)
            if len(results) >= limit:
                break
    return results
