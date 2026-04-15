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


def test_query_companies_by_route():
    kg = KnowledgeGraph()
    kg.add_company(
        name="万华化学",
        products=["MDI"],
        raw_materials=["苯胺"],
        routes=["中国-欧洲"],
    )
    kg.add_company(
        name="科思创",
        products=["MDI"],
        raw_materials=["苯胺"],
        routes=["中国-欧洲"],
    )
    companies = kg.query_companies_by_route("中国-欧洲")
    assert "万华化学" in companies
    assert "科思创" in companies


def test_knowledge_graph_load_from_seed():
    kg = KnowledgeGraph()
    companies = load_seed_companies()
    kg.load_from_seed(companies)
    routes = kg.query_routes(company="万华化学")
    assert "中国-欧洲" in routes
    assert "中国-中东" in routes


def test_query_routes_returns_empty_for_unknown_company():
    kg = KnowledgeGraph()
    assert kg.query_routes(company="不存在的公司") == []


def test_query_companies_by_route_returns_empty_for_unknown_route():
    kg = KnowledgeGraph()
    assert kg.query_companies_by_route(route="不存在的航线") == []
