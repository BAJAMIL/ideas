"""
Salla App Store Private API Client (Typed Python 3.11+)
Reverse-engineered from Salla Developer Marketplace API (https://api.salla.dev/marketplace/v2).
Provides real-time discovery of Saudi e-commerce apps, pricing, merchant demand, and ratings.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import httpx


@dataclass
class SallaCategory:
    id: str
    name: str
    type: Optional[str] = None


@dataclass
class SallaAppPlan:
    is_free: bool
    price: Optional[str]
    suffix: Optional[str]
    plan_id: Optional[int]


@dataclass
class SallaAppItem:
    id: int
    name: str
    short_description: str
    logo_url: str
    plan: SallaAppPlan
    rating_avg: float
    rating_count: int
    company_name: str
    app_url: str


class SallaMarketplaceClient:
    """Production client for Salla Marketplace APIs."""
    BASE_URL = "https://api.salla.dev/marketplace/v2"

    def __init__(self, timeout: float = 12.0):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "ar,en;q=0.9",
        }
        self.client = httpx.Client(headers=self.headers, timeout=timeout)

    def get_categories(self) -> List[SallaCategory]:
        """Fetch all official Salla marketplace categories."""
        resp = self.client.get(f"{self.BASE_URL}/categories")
        resp.raise_for_status()
        raw_items = resp.json().get("data", [])
        return [
            SallaCategory(id=str(c.get("id", "")), name=c.get("name", ""), type=c.get("type"))
            for c in raw_items
            if c.get("name")
        ]

    def list_apps(self, category_id: Optional[str] = None, page: int = 1, limit: int = 15) -> List[SallaAppItem]:
        """Fetch apps by category with price, subscription terms, and merchant ratings."""
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if category_id:
            params["category_id"] = category_id

        resp = self.client.get(f"{self.BASE_URL}/apps", params=params)
        resp.raise_for_status()
        raw_items = resp.json().get("data", [])
        
        results = []
        for a in raw_items:
            plan_raw = a.get("plan") or {}
            rev_raw = a.get("reviews") or {}
            comp_raw = a.get("company") or {}
            results.append(
                SallaAppItem(
                    id=a.get("id"),
                    name=a.get("name", ""),
                    short_description=a.get("short_description", "").strip(),
                    logo_url=a.get("logo", ""),
                    plan=SallaAppPlan(
                        is_free=bool(plan_raw.get("is_free")),
                        price=str(plan_raw.get("value")) if plan_raw.get("value") is not None else None,
                        suffix=plan_raw.get("suffix"),
                        plan_id=plan_raw.get("plan_id"),
                    ),
                    rating_avg=float(rev_raw.get("avg") or 0.0),
                    rating_count=int(rev_raw.get("count") or 0),
                    company_name=comp_raw.get("name", ""),
                    app_url=f"https://apps.salla.sa/ar/app/{a.get('id')}",
                )
            )
        return results


if __name__ == "__main__":
    client = SallaMarketplaceClient()
    print("Testing Salla Marketplace Client...")
    cats = client.get_categories()
    print(f"[+] Loaded {len(cats)} categories from Salla")
    ai_cat = next((c for c in cats if "ذكاء" in c.name), cats[1] if len(cats) > 1 else None)
    if ai_cat:
        print(f"[+] Fetching top apps for category: {ai_cat.name} (ID: {ai_cat.id})")
        apps = client.list_apps(category_id=ai_cat.id, limit=5)
        for app in apps:
            price_text = "Free" if app.plan.is_free else f"{app.plan.price} {app.plan.suffix or 'SAR'}"
            print(f" * [{app.id}] {app.name} | Price: {price_text} | Rating: {app.rating_avg}/5 ({app.rating_count} reviews)")
            print(f"   Dev: {app.company_name} | URL: {app.app_url}")
