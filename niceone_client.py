"""
Nice One Beauty & Fragrance Client (Typed Python 3.11+)
Reverse-engineered from Nice One (https://niceonesa.com).
Extracts structured beauty products, perfumes, brand names, and real-time SAR pricing from Schema JSON-LD.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import httpx
import json
import urllib.parse
from bs4 import BeautifulSoup


@dataclass
class NiceOneProduct:
    name: str
    brand: Optional[str]
    price: float
    currency: str
    availability: str
    image_url: Optional[str]
    product_url: Optional[str]


class NiceOneClient:
    """Production client for Nice One beauty and cosmetics catalog."""
    BASE_URL = "https://niceonesa.com"

    def __init__(self, timeout: float = 15.0):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept-Language": "ar,en;q=0.9",
        }
        self.client = httpx.Client(headers=self.headers, follow_redirects=True, timeout=timeout)

    def search_products(self, query: str = "عطر") -> List[NiceOneProduct]:
        """Search products on Nice One by keyword."""
        encoded = urllib.parse.quote(query)
        url = f"{self.BASE_URL}/ar/search?q={encoded}"
        resp = self.client.get(url)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        products = []

        for s in soup.find_all("script", type="application/ld+json"):
            if not s.string:
                continue
            try:
                data = json.loads(s.string)
                if data.get("@type") == "ItemList":
                    for raw in data.get("itemListElement", []):
                        offers = raw.get("offers") or {}
                        brand = raw.get("brand") or {}
                        products.append(
                            NiceOneProduct(
                                name=raw.get("name", "").strip(),
                                brand=brand.get("name") if isinstance(brand, dict) else str(brand),
                                price=float(offers.get("price") or 0.0),
                                currency=offers.get("priceCurrency", "SAR"),
                                availability="InStock" if "InStock" in str(offers.get("availability")) else "OutOfStock",
                                image_url=raw.get("image"),
                                product_url=offers.get("url"),
                            )
                        )
            except Exception:
                continue
        return products


if __name__ == "__main__":
    client = NiceOneClient()
    print("Testing Nice One Client ('عطر' / Perfume)...")
    items = client.search_products("عطر")
    print(f"[+] Retrieved {len(items)} beauty & fragrance products from Nice One:\n")
    for p in items[:4]:
        print(f" * [{p.price} {p.currency}] {p.name}")
        print(f"   Brand: {p.brand} | Status: {p.availability}")
        print(f"   URL: {p.product_url}\n")
