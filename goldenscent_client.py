"""
Golden Scent Luxury Fragrance Client (Typed Python 3.11+)
Reverse-engineered from Golden Scent (https://www.goldenscent.com).
Extracts luxury perfumes, designer brands, SKUs, and real-time prices in SAR.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import httpx
import json
import urllib.parse
from bs4 import BeautifulSoup


@dataclass
class GoldenScentProduct:
    sku: Optional[str]
    name: str
    price: float
    currency: str
    availability: str
    image_url: Optional[str]


class GoldenScentClient:
    """Production client for Golden Scent perfume catalog."""
    BASE_URL = "https://www.goldenscent.com"

    def __init__(self, timeout: float = 15.0):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept-Language": "ar,en;q=0.9",
        }
        self.client = httpx.Client(headers=self.headers, follow_redirects=True, timeout=timeout)

    def search_products(self, query: str = "عطر") -> List[GoldenScentProduct]:
        """Search perfumes and luxury fragrances on Golden Scent."""
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
                        item = raw.get("item") or {}
                        offers = item.get("offers") or {}
                        products.append(
                            GoldenScentProduct(
                                sku=item.get("sku"),
                                name=item.get("name", "").strip(),
                                price=float(offers.get("price") or 0.0),
                                currency=offers.get("priceCurrency", "SAR"),
                                availability="InStock" if "InStock" in str(offers.get("availability")) else "OutOfStock",
                                image_url=item.get("image"),
                            )
                        )
            except Exception:
                continue
        return products


if __name__ == "__main__":
    client = GoldenScentClient()
    print("Testing Golden Scent Client ('عطر' / Perfume)...")
    items = client.search_products("عطر")
    print(f"[+] Retrieved {len(items)} luxury fragrance products from Golden Scent:\n")
    for p in items[:4]:
        print(f" * [{p.price} {p.currency}] {p.name} (SKU: {p.sku or 'N/A'})")
        print(f"   Status: {p.availability} | Image: {p.image_url}\n")
