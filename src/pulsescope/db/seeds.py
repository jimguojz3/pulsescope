"""Initialize database with seed companies from JSON."""

import json
import os
from datetime import datetime

from pulsescope.db import get_db, engine
from pulsescope.db.models import Base, Company, Product, RawMaterial, Route, CompanyRoute


def _seed_path() -> str:
    """Get path to seed companies JSON."""
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "seeds", "companies.json"),
        os.path.join(os.getcwd(), "data", "seeds", "companies.json"),
    ]
    for path in candidates:
        normalized = os.path.abspath(path)
        if os.path.exists(normalized):
            return normalized
    raise FileNotFoundError("Seed company data not found")


def load_seed_companies() -> list[dict]:
    """Load seed companies from JSON file."""
    with open(_seed_path(), "r", encoding="utf-8") as f:
        return json.load(f)


def init_database():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")


def seed_database():
    """Load seed data into database."""
    companies_data = load_seed_companies()
    
    with get_db() as db:
        for c in companies_data:
            # Check if company exists
            existing = db.query(Company).filter(Company.name == c["name"]).first()
            if existing:
                print(f"Company {c['name']} already exists, skipping...")
                continue
            
            # Create company
            company = Company(
                name=c["name"],
                notes=c.get("notes", ""),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(company)
            db.flush()  # Get company.id
            
            # Create products
            for p in c.get("products", []):
                product = Product(
                    company_id=company.id,
                    name=p,
                    created_at=datetime.utcnow()
                )
                db.add(product)
            
            # Create raw materials
            for m in c.get("raw_materials", []):
                material = RawMaterial(
                    company_id=company.id,
                    name=m,
                    created_at=datetime.utcnow()
                )
                db.add(material)
            
            # Create routes and associations
            for r in c.get("routes", []):
                # Parse route string (e.g., "中国-欧洲")
                parts = r.split("-")
                if len(parts) == 2:
                    from_port, to_port = parts[0].strip(), parts[1].strip()
                    
                    # Check if route exists
                    route = db.query(Route).filter(
                        Route.from_port == from_port,
                        Route.to_port == to_port
                    ).first()
                    
                    if not route:
                        route = Route(
                            from_port=from_port,
                            to_port=to_port,
                            created_at=datetime.utcnow()
                        )
                        db.add(route)
                        db.flush()
                    
                    # Create company-route association
                    company_route = CompanyRoute(
                        company_id=company.id,
                        route_id=route.id,
                        created_at=datetime.utcnow()
                    )
                    db.add(company_route)
            
            print(f"Added company: {c['name']}")
        
        db.commit()
    
    print(f"Seeded {len(companies_data)} companies into database.")


if __name__ == "__main__":
    init_database()
    seed_database()
