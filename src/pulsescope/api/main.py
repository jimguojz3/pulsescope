"""PulseScope FastAPI with async tasks, rate limiting, and monitoring."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from pulsescope.core import analyze_company
from pulsescope.tasks import analyze_company_task
from pulsescope.logging_config import configure_logging, get_logger
from pulsescope.metrics import get_metrics, CONTENT_TYPE_LATEST, ANALYSIS_REQUESTS_TOTAL, ANALYSIS_DURATION_SECONDS
from pulsescope.cache import get_cached_risk_report, cache_risk_report

# Configure logging
configure_logging()
logger = get_logger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("PulseScope API starting up")
    yield
    logger.info("PulseScope API shutting down")


app = FastAPI(
    title="PulseScope API",
    version="0.2.0",
    description="供应链风险情报引擎 API - 支持同步/异步分析",
    lifespan=lifespan
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    company_name: str
    days_back: int = 7


class AnalyzeResponse(BaseModel):
    status: str
    reports: list
    cached: bool = False


class AsyncAnalyzeResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: dict = None


@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
@limiter.limit("10/minute")
def api_analyze(request: Request, payload: AnalyzeRequest):
    """同步分析接口 - 立即返回结果（限流：10次/分钟）."""
    import time
    start_time = time.time()
    
    try:
        # Check cache first
        cached = get_cached_risk_report(payload.company_name, payload.days_back)
        if cached:
            logger.info("Cache hit", company=payload.company_name)
            return {"status": "completed", "reports": cached, "cached": True}
        
        # Perform analysis
        reports = analyze_company(
            company_name=payload.company_name,
            days_back=payload.days_back
        )
        
        # Cache results
        if reports:
            cache_risk_report(payload.company_name, payload.days_back, reports)
        
        # Record metrics
        duration = time.time() - start_time
        ANALYSIS_DURATION_SECONDS.labels(company=payload.company_name).observe(duration)
        ANALYSIS_REQUESTS_TOTAL.labels(
            company=payload.company_name,
            status="success"
        ).inc()
        
        logger.info(
            "Analysis completed",
            company=payload.company_name,
            reports_count=len(reports),
            duration=duration
        )
        
        return {"status": "completed", "reports": reports, "cached": False}
        
    except Exception as e:
        ANALYSIS_REQUESTS_TOTAL.labels(
            company=payload.company_name,
            status="error"
        ).inc()
        logger.error("Analysis failed", company=payload.company_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analyze/async", response_model=AsyncAnalyzeResponse)
@limiter.limit("30/minute")
def api_analyze_async(request: Request, payload: AnalyzeRequest):
    """异步分析接口 - 返回任务ID，后台处理（限流：30次/分钟）."""
    try:
        # Submit task to Celery
        task = analyze_company_task.delay(
            company_name=payload.company_name,
            days_back=payload.days_back
        )
        
        logger.info(
            "Async analysis submitted",
            company=payload.company_name,
            task_id=task.id
        )
        
        return {
            "task_id": task.id,
            "status": "pending",
            "message": f"Analysis started for {payload.company_name}"
        }
        
    except Exception as e:
        logger.error("Failed to submit async task", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tasks/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str):
    """查询异步任务状态."""
    try:
        result = analyze_company_task.AsyncResult(task_id)
        
        response = {
            "task_id": task_id,
            "status": result.status,
            "result": None
        }
        
        if result.ready():
            if result.successful():
                response["result"] = result.get()
            else:
                response["status"] = "failed"
                response["result"] = {"error": str(result.result)}
        
        return response
        
    except Exception as e:
        logger.error("Failed to get task status", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/health")
def health():
    """健康检查端点."""
    from pulsescope.db import engine
    from pulsescope.cache import get_redis_client
    
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.2.0",
        "services": {}
    }
    
    # Check database
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        status["services"]["database"] = "connected"
    except Exception as e:
        status["services"]["database"] = f"error: {str(e)}"
        status["status"] = "degraded"
    
    # Check cache
    try:
        cache = get_redis_client()
        # For in-memory cache, just check it's accessible
        if hasattr(cache, 'ping'):
            cache.ping()
        status["services"]["cache"] = "connected"
    except Exception as e:
        status["services"]["cache"] = f"error: {str(e)}"
        status["status"] = "degraded"
    
    return status


@app.get("/api/v1/metrics")
def metrics():
    """Prometheus 监控指标端点."""
    return Response(
        content=get_metrics(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/api/v1/companies")
def list_companies():
    """获取已注册的企业列表."""
    from pulsescope.db import get_db
    from pulsescope.db.models import Company
    
    with get_db() as db:
        companies = db.query(Company).all()
        return {
            "companies": [
                {
                    "id": c.id,
                    "name": c.name,
                    "stock_code": c.stock_code,
                    "industry": c.industry
                }
                for c in companies
            ]
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
