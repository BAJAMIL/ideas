"""
Lulu Hypermarket KSA Discovery Client
Direct JSON Endpoint API on Akinon Commerce Engine
Domain: gcc.luluhypermarket.com/en-sa/
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import httpx


@dataclass
class LuluProduct:
    sku: str
    name: str
    price: float
    original_price: float
    discount_amount: float
    in_stock: bool
    stock_count: int
    brand: Optional[str]
    category: Optional[str]
    url: str
    image_url: Optional[str]
    specs: Dict[str, Any]


class LuluClient:
    BASE_URL = "https://gcc.luluhypermarket.com/en-sa"

    def __init__(self, timeout: float = 12.0):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en,ar;q=0.9",
        }
        self.client = httpx.Client(headers=self.headers, follow_redirects=True, timeout=timeout)

    def search_products(self, query: str = "", page: int = 1) -> Dict[str, Any]:
        """Search products with pagination and full hardware/grocery attributes."""
        url = f"{self.BASE_URL}/list/"
        params: Dict[str, Any] = {"format": "json", "page": page}
        if query:
            params["search_text"] = query

        resp = self.client.get(url, params=params)
        if resp.status_code != 200:
            return {"total": 0, "products": []}

        try:
            data = resp.json()
            total = data.get("pagination", {}).get("total_count", 0)
            raw_products = data.get("products", [])
            products: List[LuluProduct] = []

            for p in raw_products:
                attrs = p.get("attributes", {})
                kwargs = p.get("attributes_kwargs", {})
                brand = kwargs.get("brand", {}).get("value") or attrs.get("brand")
                cat = kwargs.get("level_3", {}).get("value") or kwargs.get("level_1", {}).get("value")

                images = p.get("productimage_set", [])
                image_url = images[0].get("image") if images else None
                abs_url = p.get("absolute_url")
                full_url = f"https://gcc.luluhypermarket.com/en-sa{abs_url}" if abs_url else ""

                price = float(p.get("price", 0.0) or 0.0)
                retail = float(p.get("retail_price", 0.0) or price)
                disc = float(p.get("discount_amount", 0.0) or 0.0)

                products.append(
                    LuluProduct(
                        sku=str(p.get("sku", "")),
                        name=str(p.get("name", "")),
                        price=price,
                        original_price=retail,
                        discount_amount=disc,
                        in_stock=bool(p.get("in_stock", True)),
                        stock_count=int(p.get("stock", 0) or 0),
                        brand=brand,
                        category=cat,
                        url=full_url,
                        image_url=image_url,
                        specs={
                            "storage": kwargs.get("internal_storage", {}).get("value"),
                            "color": kwargs.get("color", {}).get("value"),
                            "screen_size": kwargs.get("screen_size", {}).get("value"),
                            "os": kwargs.get("os", {}).get("value"),
                        },
                    )
                )

            return {"total": total, "products": products}
        except Exception:
            return {"total": 0, "products": []}


if __name__ == "__main__":
    client = LuluClient()
    res = client.search_products("iphone", page=1)
    print(f"Lulu KSA Found: {res['total']} items. Showing first:")
    for prod in res["products"][:2]:
        print(f" - {prod.name} | {prod.price:.2f} SAR | SKU: {prod.sku} | In Stock: {prod.stock_count}")
