"""Database models for PulseScope."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship

from pulsescope.db import Base


class Company(Base):
    """Company entity in the knowledge graph."""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    stock_code = Column(String(20), nullable=True)
    industry = Column(String(50), nullable=True)
    market_cap = Column(Float, nullable=True)  # in billions
    export_ratio = Column(Float, nullable=True)  # 0-1
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = relationship("Product", back_populates="company")
    raw_materials = relationship("RawMaterial", back_populates="company")
    routes = relationship("CompanyRoute", back_populates="company")
    risk_reports = relationship("RiskReport", back_populates="company")
    
    __table_args__ = (
        Index('idx_company_industry', 'industry'),
    )


class Product(Base):
    """Product that a company produces."""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)
    spot_price_symbol = Column(String(50), nullable=True)
    futures_symbol = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("Company", back_populates="products")


class RawMaterial(Base):
    """Raw material that a company consumes."""
    __tablename__ = "raw_materials"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    material_type = Column(String(50), nullable=True)
    spot_price_symbol = Column(String(50), nullable=True)
    consumption_ratio = Column(Float, nullable=True)  # proportion of total cost
    created_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("Company", back_populates="raw_materials")


class Route(Base):
    """Shipping route between ports."""
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True)
    from_port = Column(String(100), nullable=False)
    to_port = Column(String(100), nullable=False)
    distance_nm = Column(Float, nullable=True)  # nautical miles
    typical_duration_days = Column(Float, nullable=True)
    route_type = Column(String(50), nullable=True)  # e.g., "container", "tanker"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    companies = relationship("CompanyRoute", back_populates="route")
    
    __table_args__ = (
        Index('idx_route_ports', 'from_port', 'to_port'),
    )


class CompanyRoute(Base):
    """Association table: which companies use which routes."""
    __tablename__ = "company_routes"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    usage_ratio = Column(Float, nullable=True)  # proportion of shipments on this route
    created_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("Company", back_populates="routes")
    route = relationship("Route", back_populates="companies")


class Event(Base):
    """Risk event extracted from news/announcements."""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    source = Column(String(200), nullable=False)
    source_type = Column(String(50), nullable=False)  # "news", "announcement", "shipping", "price"
    event_type = Column(String(50), nullable=False)  # "geopolitical", "natural_disaster", "policy", "price", "operational"
    impact_area = Column(String(50), nullable=False)  # "shipping", "energy", "raw_materials", "market"
    event_date = Column(DateTime, nullable=False)
    location = Column(String(200), nullable=True)
    severity_score = Column(Float, nullable=True)  # 0-100
    raw_metadata = Column(JSON, nullable=True)  # original source data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    risk_reports = relationship("RiskReport", back_populates="event")
    
    __table_args__ = (
        Index('idx_event_date_type', 'event_date', 'event_type'),
        Index('idx_event_location', 'location'),
    )


class RiskReport(Base):
    """Generated risk analysis report."""
    __tablename__ = "risk_reports"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    risk_level = Column(String(10), nullable=False)  # "高", "中", "低"
    risk_score = Column(Float, nullable=True)  # 0-100
    confidence = Column(String(10), nullable=True)  # "高", "中", "低"
    reasoning = Column(Text, nullable=False)
    impact_chain = Column(JSON, nullable=False, default=list)  # list of strings
    suggested_metrics = Column(JSON, nullable=False, default=list)  # list of strings
    cache_key = Column(String(64), nullable=True, index=True)  # for deduplication
    created_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("Company", back_populates="risk_reports")
    event = relationship("Event", back_populates="risk_reports")
    
    __table_args__ = (
        Index('idx_report_company_date', 'company_id', 'created_at'),
        Index('idx_report_cache', 'cache_key'),
    )


class PriceData(Base):
    """Time-series price data for commodities/futures."""
    __tablename__ = "price_data"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=True)
    price_type = Column(String(20), nullable=False)  # "spot", "futures", "index"
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="CNY")
    volume = Column(Float, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    source = Column(String(100), nullable=True)
    extra_data = Column(JSON, nullable=True)  # Renamed from 'metadata'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_price_symbol_time', 'symbol', 'timestamp'),
    )


class CacheEntry(Base):
    """Generic cache entries for expensive operations."""
    __tablename__ = "cache_entries"
    
    id = Column(Integer, primary_key=True)
    cache_key = Column(String(128), unique=True, nullable=False, index=True)
    cache_type = Column(String(50), nullable=False)  # "news", "report", "graph_node"
    data = Column(JSON, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_cache_type_expires', 'cache_type', 'expires_at'),
    )
