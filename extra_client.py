"""
eXtra (United Electronics) Private API Client (Typed Python 3.11+)
Reverse-engineered from eXtra KSA (https://www.extra.com/en-sa/).
Powered by eXtra's live AI Discovery & Search Engine (Unbxd).

Features:
- Dual Arabic (ar-SA) and English (en-SA) search indexes.
- Real-time electronics pricing (SAR), discounts, wasPrice, and clearance deals.
- Instant brand matching, category identification, and stock status.
- Key tool for identifying physical product margin opportunities and accessory bundles.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import httpx


@dataclass
class ExtraProduct:
    sku: str
    title: str
    price: float
    was_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    currency: str = "SAR"
    brand: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    in_stock: bool = True
    raw_data: Dict[str, Any] = field(default_factory=dict)


class ExtraClient:
    """Production client for eXtra KSA's search & product catalog APIs."""

    API_BASE = "https://search.unbxd.io"
    SITE_CONFIG = {
        "en": {
            "siteKey": "ss-unbxd-auk-extra-saudi-en-prod11541714990488",
            "apiKey": "21705619e273429e5767eea44ccb1ad5",
        },
        "ar": {
            "siteKey": "ss-unbxd-auk-extra-saudi-ar-prod11541714990564",
            "apiKey": "8fb45132f31d81ab46966cc135c24430",
        },
    }
    EXTRA_BASE_URL = "https://www.extra.com"

    def __init__(self, timeout: float = 12.0):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
            "Accept-Language": "ar,en;q=0.9",
        }
        self.client = httpx.Client(headers=self.headers, timeout=timeout)

    def _get_credentials(self, lang: str) -> Dict[str, str]:
        normalized = lang.lower()[:2]
        return self.SITE_CONFIG.get(normalized, self.SITE_CONFIG["en"])

    def search_products(
        self,
        query: str,
        lang: str = "en",
        rows: int = 24,
        start: int = 0,
        sort_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Searches products in eXtra KSA.

        Args:
            query: Keyword to search (e.g. 'laptop', 'tv', 'مكيف', 'ايفون').
            lang: 'en' for English catalog, 'ar' for Arabic catalog.
            rows: Number of results to return (default 24).
            start: Offset for pagination (0-indexed).
            sort_by: Optional sort string (e.g. 'price asc', 'price desc', 'rating desc').
        """
        creds = self._get_credentials(lang)
        api_key = creds["apiKey"]
        site_key = creds["siteKey"]

        url = f"{self.API_BASE}/{api_key}/{site_key}/search"
        params: Dict[str, Any] = {
            "q": query,
            "rows": rows,
            "start": start,
        }
        if sort_by:
            params["sort"] = sort_by

        resp = self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json().get("response", {})

        total_products = data.get("numberOfProducts", 0)
        items: List[ExtraProduct] = []

        for p in data.get("products", []):
            price_val = float(p.get("price", 0.0) or 0.0)
            was_price_val = float(p.get("wasPrice", 0.0) or 0.0) if p.get("wasPrice") else None

            discount = None
            if was_price_val and was_price_val > price_val:
                discount = round(((was_price_val - price_val) / was_price_val) * 100, 1)

            brand_val = p.get("brand")
            if isinstance(brand_val, list):
                brand_val = ", ".join(brand_val)

            rel_url = p.get("urlEn" if lang == "en" else "urlAr") or p.get("urlEn")
            full_url = f"{self.EXTRA_BASE_URL}/{lang}-sa/{rel_url.lstrip('/')}" if rel_url else None

            items.append(
                ExtraProduct(
                    sku=str(p.get("uniqueId") or p.get("sku") or ""),
                    title=p.get("title", ""),
                    price=price_val,
                    was_price=was_price_val,
                    discount_percentage=discount,
                    brand=brand_val,
                    url=full_url,
                    image_url=p.get("imageUrl") or p.get("amplienceProductBaseUrl"),
                    in_stock=p.get("inStock", True),
                    raw_data=p,
                )
            )

        return {
            "total": total_products,
            "start": start,
            "products": items,
            "facets": data.get("facets", {}),
        }

    def fetch_top_discounts(self, category_query: str = "laptop", lang: str = "en", limit: int = 5) -> List[ExtraProduct]:
        """Fetch products with the largest discounts from eXtra."""
        res = self.search_products(category_query, lang=lang, rows=limit * 3)
        products = res.get("products", [])
        discounted = [p for p in products if p.discount_percentage and p.discount_percentage > 0]
        discounted.sort(key=lambda p: p.discount_percentage or 0, reverse=True)
        return discounted[:limit]


def fetch_extra_consumer_signals(max_items: int = 10) -> List[Dict[str, Any]]:
    """Standard discovery hook for BAJAMIL Ideas agent."""
    signals = []
    client = ExtraClient()

    targets = [
        ("gaming laptop", "en", "Gaming Laptops"),
        ("شاشة ذكية", "ar", "Smart Displays & TVs"),
        ("قهوة", "ar", "Specialty Coffee Machines"),
    ]

    for q, lang, cat in targets:
        try:
            res = client.search_products(q, lang=lang, rows=max_items)
            for p in res.get("products", [])[:3]:
                sig = {
                    "title": f"eXtra {cat}: {p.title}",
                    "price_sar": p.price,
                    "url": p.url,
                    "sku": p.sku,
                    "brand": p.brand,
                    "source": "eXtra Stores (extra.com)",
                    "type": "CONSUMER_BENCHMARK",
                }
                if p.discount_percentage:
                    sig["discount_pct"] = p.discount_percentage
                signals.append(sig)
        except Exception:
            continue

    return signals
