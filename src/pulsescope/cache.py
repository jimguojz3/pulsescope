"""Cache layer for PulseScope using Redis with fallback to in-memory."""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional
from collections import OrderedDict

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from pulsescope.db import get_db
from pulsescope.db.models import CacheEntry


class InMemoryCache:
    """LRU in-memory cache for development environments without Redis."""
    
    def __init__(self, max_size: int = 1000):
        self._data: OrderedDict[str, tuple[Any, datetime]] = OrderedDict()
        self._max_size = max_size
    
    def get(self, key: str) -> Optional[str]:
        now = datetime.utcnow()
        if key in self._data:
            value, expires_at = self._data[key]
            if expires_at > now:
                # Move to end (LRU)
                self._data.move_to_end(key)
                return json.dumps(value, default=str)
            else:
                del self._data[key]
        return None
    
    def setex(self, key: str, ttl_seconds: int, value: str):
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        # Evict oldest if at capacity
        if len(self._data) >= self._max_size and key not in self._data:
            self._data.popitem(last=False)
        self._data[key] = (json.loads(value), expires_at)
    
    def delete(self, key: str):
        self._data.pop(key, None)


def get_redis_client():
    """Get Redis client or in-memory fallback."""
    import os
    
    if not REDIS_AVAILABLE:
        return InMemoryCache()
    
    try:
        host = os.environ.get("REDIS_HOST", "localhost")
        port = int(os.environ.get("REDIS_PORT", 6379))
        db = int(os.environ.get("REDIS_DB", 0))
        client = redis.Redis(host=host, port=port, db=db, decode_responses=True, socket_connect_timeout=2)
        # Test connection
        client.ping()
        return client
    except (redis.RedisError, Exception):
        # Fallback to in-memory cache
        return InMemoryCache()


class Cache:
    """Multi-layer cache: L1 Redis, L2 PostgreSQL (fallback)."""
    
    def __init__(self):
        self._redis = get_redis_client()
    
    def _make_key(self, prefix: str, *parts: str) -> str:
        """Create a cache key from parts."""
        content = "|".join(str(p) for p in parts)
        hash_suffix = hashlib.md5(content.encode()).hexdigest()[:12]
        return f"pulsescope:{prefix}:{hash_suffix}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        # Try Redis first
        try:
            value = self._redis.get(key)
            if value:
                return json.loads(value)
        except redis.RedisError:
            pass  # Fall through to DB cache
        
        # Try PostgreSQL as fallback
        with get_db() as db:
            entry = db.query(CacheEntry).filter(
                CacheEntry.cache_key == key,
                CacheEntry.expires_at > datetime.utcnow()
            ).first()
            if entry:
                return entry.data
        
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int):
        """Set value in cache with TTL."""
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        
        # Write to Redis
        try:
            self._redis.setex(key, ttl_seconds, json.dumps(value, default=str))
        except redis.RedisError:
            pass  # Continue to write to DB
        
        # Write to PostgreSQL as persistent cache
        with get_db() as db:
            # Determine cache type from key prefix
            parts = key.split(":")
            cache_type = parts[1] if len(parts) > 1 else "default"
            
            # Upsert
            existing = db.query(CacheEntry).filter(CacheEntry.cache_key == key).first()
            if existing:
                existing.data = value
                existing.expires_at = expires_at
            else:
                entry = CacheEntry(
                    cache_key=key,
                    cache_type=cache_type,
                    data=value,
                    expires_at=expires_at
                )
                db.add(entry)
    
    def delete(self, key: str):
        """Delete value from cache."""
        try:
            self._redis.delete(key)
        except redis.RedisError:
            pass
        
        with get_db() as db:
            db.query(CacheEntry).filter(CacheEntry.cache_key == key).delete()
    
    def clear_expired(self):
        """Clear expired entries from DB cache."""
        with get_db() as db:
            db.query(CacheEntry).filter(CacheEntry.expires_at < datetime.utcnow()).delete()


# Convenience functions for specific cache types

def cache_news_search(query: str, days_back: int, results: list) -> str:
    """Cache Tavily news search results."""
    cache = Cache()
    key = cache._make_key("news", query, str(days_back))
    cache.set(key, results, ttl_seconds=3600)  # 1 hour
    return key


def get_cached_news_search(query: str, days_back: int) -> Optional[list]:
    """Get cached news search results."""
    cache = Cache()
    key = cache._make_key("news", query, str(days_back))
    return cache.get(key)


def cache_risk_report(company_name: str, days_back: int, reports: list) -> str:
    """Cache risk analysis reports."""
    cache = Cache()
    key = cache._make_key("report", company_name, str(days_back))
    cache.set(key, reports, ttl_seconds=1800)  # 30 minutes
    return key


def get_cached_risk_report(company_name: str, days_back: int) -> Optional[list]:
    """Get cached risk reports."""
    cache = Cache()
    key = cache._make_key("report", company_name, str(days_back))
    return cache.get(key)


def cache_graph_node(node_type: str, node_name: str, data: dict) -> str:
    """Cache knowledge graph node data."""
    cache = Cache()
    key = cache._make_key("graph", node_type, node_name)
    cache.set(key, data, ttl_seconds=86400)  # 24 hours
    return key


def get_cached_graph_node(node_type: str, node_name: str) -> Optional[dict]:
    """Get cached graph node data."""
    cache = Cache()
    key = cache._make_key("graph", node_type, node_name)
    return cache.get(key)
