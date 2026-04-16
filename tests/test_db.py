"""Tests for database layer."""

from datetime import datetime

import pytest

from pulsescope.db import get_db, engine
from pulsescope.db.models import Base, Company, Product, Event, RiskReport


@pytest.fixture(scope="module")
def setup_database():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup - drop tables after tests
    Base.metadata.drop_all(bind=engine)


class TestCompanyModel:
    def test_create_company(self, setup_database):
        with get_db() as db:
            company = Company(
                name="测试公司",
                stock_code="TEST001",
                industry="化工",
                notes="Test notes"
            )
            db.add(company)
            db.flush()
            
            assert company.id is not None
            assert company.name == "测试公司"
            assert company.created_at is not None
    
    def test_company_products_relationship(self, setup_database):
        with get_db() as db:
            company = Company(name="产品测试公司")
            db.add(company)
            db.flush()
            
            product = Product(company_id=company.id, name="MDI", category="化工原料")
            db.add(product)
            db.commit()
            
            # Query fresh company to get relationships
            fresh_company = db.query(Company).filter_by(id=company.id).first()
            assert len(fresh_company.products) == 1
            assert fresh_company.products[0].name == "MDI"


class TestEventModel:
    def test_create_event(self, setup_database):
        with get_db() as db:
            event = Event(
                title="霍尔木兹海峡封锁",
                source="Reuters",
                source_type="news",
                event_type="geopolitical",
                impact_area="shipping",
                event_date=datetime.utcnow(),
                location="伊朗"
            )
            db.add(event)
            db.flush()
            
            assert event.id is not None
            assert event.title == "霍尔木兹海峡封锁"


class TestRiskReportModel:
    def test_create_risk_report(self, setup_database):
        with get_db() as db:
            # Create company first
            company = Company(name="风险测试公司")
            db.add(company)
            db.flush()
            
            report = RiskReport(
                company_id=company.id,
                risk_level="高",
                risk_score=85.0,
                confidence="中",
                reasoning="航运中断风险",
                impact_chain=["事件1", "事件2"],
                suggested_metrics=["BDI", "运费指数"]
            )
            db.add(report)
            db.flush()
            
            assert report.id is not None
            assert report.risk_score == 85.0
            assert report.impact_chain == ["事件1", "事件2"]
