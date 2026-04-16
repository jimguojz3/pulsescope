"""Tests for cache layer."""

import pytest
from datetime import datetime, timedelta

from pulsescope.db import Base, engine
from pulsescope.cache import (
    Cache,
    InMemoryCache,
    cache_news_search,
    get_cached_news_search,
    cache_risk_report,
    get_cached_risk_report,
)


@pytest.fixture(scope="module")
def setup_database():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup - drop tables after tests
    Base.metadata.drop_all(bind=engine)


class TestInMemoryCache:
    def test_cache_get_set(self):
        cache = InMemoryCache()
        cache.setex("key1", 60, '{"data": "value"}')
        result = cache.get("key1")
        assert result == '{"data": "value"}'
    
    def test_cache_expires(self):
        cache = InMemoryCache()
        cache.setex("key1", 0, '{"data": "value"}')  # Immediate expire
        result = cache.get("key1")
        assert result is None
    
    def test_cache_delete(self):
        cache = InMemoryCache()
        cache.setex("key1", 60, '{"data": "value"}')
        cache.delete("key1")
        result = cache.get("key1")
        assert result is None
    
    def test_cache_lru_eviction(self):
        cache = InMemoryCache(max_size=2)
        cache.setex("key1", 60, '{"data": "1"}')
        cache.setex("key2", 60, '{"data": "2"}')
        cache.setex("key3", 60, '{"data": "3"}')  # Should evict key1
        
        assert cache.get("key1") is None
        assert cache.get("key2") is not None
        assert cache.get("key3") is not None


class TestCacheLayer:
    def test_cache_news_roundtrip(self, setup_database):
        news_data = [{"title": "Test", "content": "Content"}]
        cache_news_search("query", 7, news_data)
        
        cached = get_cached_news_search("query", 7)
        assert cached == news_data
    
    def test_cache_report_roundtrip(self, setup_database):
        reports = [{"company": "Test", "risk_level": "高"}]
        cache_risk_report("TestCorp", 7, reports)
        
        cached = get_cached_risk_report("TestCorp", 7)
        assert cached == reports
    
    def test_cache_miss_returns_none(self, setup_database):
        result = get_cached_news_search("nonexistent", 7)
        assert result is None
