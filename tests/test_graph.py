import json
import os

from pulsescope.knowledge.graph import KnowledgeGraph
from pulsescope.knowledge.seeds import load_seed_companies


def test_load_seed_companies():
    data = load_seed_companies()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "name" in data[0]
    assert "products" in data[0]


def test_knowledge_graph_builds_and_queries():
    kg = KnowledgeGraph()
    kg.add_company(
        name="万华化学",
        products=["MDI", "TDI"],
        raw_materials=["苯胺", "甲苯"],
        routes=["中国-欧洲", "中国-中东"],
    )
    related = kg.query_routes(company="万华化学")
    assert "中国-欧洲" in related
    assert "中国-中东" in related
