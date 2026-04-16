"""Tests for API endpoints with async tasks and monitoring."""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from pulsescope.api.main import app
from pulsescope.db import Base, engine
from pulsescope.db.models import Company

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestHealthEndpoint:
    def test_health_check(self, setup_database):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "timestamp" in data
        assert "services" in data
        assert "database" in data["services"]
        assert "cache" in data["services"]


class TestCompaniesEndpoint:
    def test_list_companies(self, setup_database):
        # First, add a company
        from pulsescope.db import get_db
        with get_db() as db:
            company = Company(name="API测试公司", stock_code="API001", industry="化工")
            db.add(company)
        
        response = client.get("/api/v1/companies")
        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        assert len(data["companies"]) >= 1


class TestAnalyzeEndpoint:
    @patch("pulsescope.api.main.get_cached_risk_report")
    @patch("pulsescope.api.main.analyze_company")
    @patch("pulsescope.api.main.cache_risk_report")
    def test_analyze_sync_success(self, mock_cache_set, mock_analyze, mock_cache_get, setup_database):
        # No cache hit
        mock_cache_get.return_value = None
        
        # Mock analysis result
        mock_analyze.return_value = [
            {
                "company": "万华化学",
                "event": "测试事件",
                "risk_level": "中",
                "reasoning": "测试推理"
            }
        ]
        
        response = client.post(
            "/api/v1/analyze",
            json={"company_name": "万华化学", "days_back": 7}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["cached"] == False
        assert len(data["reports"]) == 1
        
        mock_analyze.assert_called_once_with(company_name="万华化学", days_back=7)
        mock_cache_set.assert_called_once()
    
    @patch("pulsescope.api.main.get_cached_risk_report")
    def test_analyze_cache_hit(self, mock_cache_get, setup_database):
        # Cache hit
        cached_reports = [
            {
                "company": "万华化学",
                "risk_level": "高",
                "reasoning": "缓存结果"
            }
        ]
        mock_cache_get.return_value = cached_reports
        
        response = client.post(
            "/api/v1/analyze",
            json={"company_name": "万华化学", "days_back": 7}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["cached"] == True
        assert data["reports"] == cached_reports
    
    def test_analyze_missing_company(self, setup_database):
        response = client.post(
            "/api/v1/analyze",
            json={"days_back": 7}
        )
        assert response.status_code == 422  # Validation error


class TestAsyncAnalyzeEndpoint:
    @patch("pulsescope.api.main.analyze_company_task")
    def test_analyze_async_submit(self, mock_task, setup_database):
        # Mock Celery task
        mock_task.delay.return_value = MagicMock(id="test-task-123")
        
        response = client.post(
            "/api/v1/analyze/async",
            json={"company_name": "万华化学", "days_back": 7}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-123"
        assert data["status"] == "pending"
        
        mock_task.delay.assert_called_once_with(company_name="万华化学", days_back=7)


class TestMetricsEndpoint:
    def test_metrics(self, setup_database):
        response = client.get("/api/v1/metrics")
        assert response.status_code == 200
        # Prometheus format check
        assert "pulsescope_" in response.text or "# HELP" in response.text or response.text == ""
