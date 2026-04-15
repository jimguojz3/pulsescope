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
        name="\u4e07\u534e\u5316\u5b66",
        products=["MDI", "TDI"],
        raw_materials=["\u82ef\u80fa", "\u7532\u82ef"],
        routes=["\u4e2d\u56fd-\u6b27\u6d32", "\u4e2d\u56fd-\u4e2d\u4e1c"],
    )
    related = kg.query_routes(company="\u4e07\u534e\u5316\u5b66")
    assert "\u4e2d\u56fd-\u6b27\u6d32" in related
    assert "\u4e2d\u56fd-\u4e2d\u4e1c" in related


def test_query_products_and_materials():
    kg = KnowledgeGraph()
    kg.add_company(
        name="\u4e07\u534e\u5316\u5b66",
        products=["MDI", "TDI"],
        raw_materials=["\u82ef\u80fa", "\u7532\u82ef"],
        routes=["\u4e2d\u56fd-\u6b27\u6d32"],
    )
    products = kg.query_products("\u4e07\u534e\u5316\u5b66")
    materials = kg.query_materials("\u4e07\u534e\u5316\u5b66")
    assert "MDI" in products
    assert "TDI" in products
    assert "\u82ef\u80fa" in materials
    assert "\u7532\u82ef" in materials


def test_query_products_and_materials_return_empty_for_unknown_company():
    kg = KnowledgeGraph()
    assert kg.query_products("\u4e0d\u5b58\u5728") == []
    assert kg.query_materials("\u4e0d\u5b58\u5728") == []


def test_query_companies_by_route():
    kg = KnowledgeGraph()
    kg.add_company(
        name="\u4e07\u534e\u5316\u5b66",
        products=["MDI"],
        raw_materials=["\u82ef\u80fa"],
        routes=["\u4e2d\u56fd-\u6b27\u6d32"],
    )
    kg.add_company(
        name="\u79d1\u601d\u521b",
        products=["MDI"],
        raw_materials=["\u82ef\u80fa"],
        routes=["\u4e2d\u56fd-\u6b27\u6d32"],
    )
    companies = kg.query_companies_by_route("\u4e2d\u56fd-\u6b27\u6d32")
    assert "\u4e07\u534e\u5316\u5b66" in companies
    assert "\u79d1\u601d\u521b" in companies


def test_knowledge_graph_load_from_seed():
    kg = KnowledgeGraph()
    companies = load_seed_companies()
    kg.load_from_seed(companies)
    routes = kg.query_routes(company="\u4e07\u534e\u5316\u5b66")
    assert "\u4e2d\u56fd-\u6b27\u6d32" in routes
    assert "\u4e2d\u56fd-\u4e2d\u4e1c" in routes


def test_query_routes_returns_empty_for_unknown_company():
    kg = KnowledgeGraph()
    assert kg.query_routes(company="\u4e0d\u5b58\u5728\u7684\u516c\u53f8") == []


def test_query_companies_by_route_returns_empty_for_unknown_route():
    kg = KnowledgeGraph()
    assert kg.query_companies_by_route(route="\u4e0d\u5b58\u5728\u7684\u822a\u7ebf") == []
