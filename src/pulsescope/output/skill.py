from mcp.server.fastmcp import FastMCP

from pulsescope.core import analyze_company

mcp_app = FastMCP("pulsescope")


@mcp_app.tool()
def analyze_company_risk(company_name: str, days_back: int = 7) -> str:
    """Analyze supply chain risk for a given company based on recent news and announcements.

    Args:
        company_name: The Chinese name of the company to analyze (e.g. "万华化学").
        days_back: How many days of recent information to scan. Default is 7.

    Returns:
        A JSON-formatted risk report string.
    """
    import json

    reports = analyze_company(company_name=company_name, days_back=days_back)
    if not reports:
        return json.dumps({"status": "no_risk_events_detected", "company": company_name}, ensure_ascii=False)
    return json.dumps(reports, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp_app.run()
