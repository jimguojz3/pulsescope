import networkx as nx


class KnowledgeGraph:
    def __init__(self):
        self._g = nx.Graph()

    def add_company(self, name: str, products: list[str], raw_materials: list[str], routes: list[str]):
        self._g.add_node(name, node_type="company")
        for p in products:
            self._g.add_node(p, node_type="product")
            self._g.add_edge(name, p, relation="produces")
        for m in raw_materials:
            self._g.add_node(m, node_type="material")
            self._g.add_edge(name, m, relation="uses")
        for r in routes:
            self._g.add_node(r, node_type="route")
            self._g.add_edge(name, r, relation="ships_via")

    def query_routes(self, company: str) -> list[str]:
        if company not in self._g:
            return []
        neighbors = self._g.neighbors(company)
        return [n for n in neighbors if self._g.nodes[n].get("node_type") == "route"]

    def query_companies_by_route(self, route: str) -> list[str]:
        if route not in self._g:
            return []
        neighbors = self._g.neighbors(route)
        return [n for n in neighbors if self._g.nodes[n].get("node_type") == "company"]

    def load_from_seed(self, companies: list[dict]):
        for c in companies:
            self.add_company(
                name=c["name"],
                products=c.get("products", []),
                raw_materials=c.get("raw_materials", []),
                routes=c.get("routes", []),
            )
