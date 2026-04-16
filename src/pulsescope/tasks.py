"""Background tasks for PulseScope."""

import structlog
from typing import List, Optional

from pulsescope.celery_app import celery_app
from pulsescope.core import analyze_company as _analyze_company
from pulsescope.cache import cache_risk_report
from pulsescope.db import get_db
from pulsescope.db.models import RiskReport, Company

logger = structlog.get_logger(__name__)


@celery_app.task(bind=True, max_retries=3)
def analyze_company_task(self, company_name: str, days_back: int = 7) -> dict:
    """Analyze company risk asynchronously.
    
    Args:
        company_name: Name of the company to analyze
        days_back: Number of days to look back
        
    Returns:
        Task result containing reports or error info
    """
    try:
        logger.info("Starting analysis", company=company_name, days_back=days_back)
        
        # Check cache first
        from pulsescope.cache import get_cached_risk_report
        cached = get_cached_risk_report(company_name, days_back)
        if cached:
            logger.info("Returning cached result", company=company_name)
            return {
                "status": "completed",
                "source": "cache",
                "company": company_name,
                "reports": cached
            }
        
        # Perform analysis
        reports = _analyze_company(company_name=company_name, days_back=days_back)
        
        # Cache results
        if reports:
            cache_risk_report(company_name, days_back, reports)
            
            # Store in database
            with get_db() as db:
                company = db.query(Company).filter(Company.name == company_name).first()
                company_id = company.id if company else None
                
                for report in reports:
                    db_report = RiskReport(
                        company_id=company_id,
                        event_id=None,  # TODO: link to actual event
                        risk_level=report.get("risk_level", "未知"),
                        risk_score=None,  # TODO: extract from report
                        confidence=None,
                        reasoning=report.get("reasoning", ""),
                        impact_chain=report.get("impact_chain", []),
                        suggested_metrics=report.get("suggested_metrics", []),
                    )
                    db.add(db_report)
        
        logger.info("Analysis completed", company=company_name, reports_count=len(reports))
        
        return {
            "status": "completed",
            "source": "fresh",
            "company": company_name,
            "reports": reports
        }
        
    except Exception as exc:
        logger.error("Analysis failed", company=company_name, error=str(exc))
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@celery_app.task
def clear_expired_cache() -> dict:
    """Periodic task to clear expired cache entries."""
    from pulsescope.cache import Cache
    cache = Cache()
    cache.clear_expired()
    return {"status": "completed", "action": "clear_expired_cache"}


@celery_app.task
def cleanup_old_reports(days: int = 30) -> dict:
    """Remove old risk reports from database."""
    from datetime import datetime, timedelta
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    with get_db() as db:
        from pulsescope.db.models import RiskReport
        deleted = db.query(RiskReport).filter(RiskReport.created_at < cutoff).delete()
        
    logger.info("Cleaned up old reports", deleted_count=deleted, days=days)
    return {"status": "completed", "deleted": deleted}
