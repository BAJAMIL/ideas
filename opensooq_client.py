"""
OpenSooq Saudi Arabia Private Client (Typed Python 3.11+)
Reverse-engineered from OpenSooq's Next.js SSR state (sa.opensooq.com).
Extracts classified listings, seller ratings, WhatsApp contact badges, and direct pricing.
"""

import httpx
import re
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class OpenSooqSeller:
    id: Optional[int]
    name: Optional[str]
    username: Optional[str]
    rating: float
    rating_count: int
    verification_level: Optional[int]


@dataclass
class OpenSooqListing:
    id: int
    title: str
    price_raw: Optional[str]
    currency: str
    city: str
    neighborhood: Optional[str]
    category: str
    posted_at: Optional[str]
    seller: OpenSooqSeller
    has_whatsapp: bool
    has_chat: bool
    url: str
    description: Optional[str]
    image_count: int


class OpenSooqClient:
    """Production client for OpenSooq (Saudi Arabia)."""
    BASE_URL = "https://sa.opensooq.com"

    def __init__(self, timeout: float = 15.0):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept-Language": "ar,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        self.client = httpx.Client(headers=self.headers, follow_redirects=True, timeout=timeout)

    def search(self, query: str = "", category_id: Optional[int] = None, page: int = 1) -> List[OpenSooqListing]:
        """Search OpenSooq KSA by keyword or category with pagination."""
        params = []
        if query:
            params.append(f"PostSearch[term]={query}")
        if category_id:
            params.append(f"PostSearch[category_id]={category_id}")
        if page > 1:
            params.append(f"page={page}")
        query_str = f"?{'&'.join(params)}" if params else ""
        
        url = f"{self.BASE_URL}/ar/find{query_str}"
        resp = self.client.get(url)
        if resp.status_code != 200:
            return []

        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', resp.text)
        if not m:
            return []

        try:
            data = json.loads(m.group(1))
            listings = data.get("props", {}).get("pageProps", {}).get("serpApiResponse", {}).get("listings", {})
            raw_items = listings.get("items", []) if isinstance(listings, dict) else []
            
            clean_results = []
            for item in raw_items:
                badges = item.get("post_badges") or []
                clean_results.append(
                    OpenSooqListing(
                        id=item.get("id"),
                        title=item.get("title", "").strip(),
                        price_raw=item.get("price_amount"),
                        currency=item.get("price_currency_iso", "SAR"),
                        city=item.get("city_label", ""),
                        neighborhood=item.get("nhood_label"),
                        category=f"{item.get('cat1_label')} > {item.get('cat2_label')}",
                        posted_at=item.get("posted_at"),
                        seller=OpenSooqSeller(
                            id=item.get("member_id"),
                            name=item.get("member_display_name"),
                            username=item.get("member_user_name"),
                            rating=float(item.get("member_rating_avg") or 0.0),
                            rating_count=int(item.get("member_rating_count") or 0),
                            verification_level=item.get("verification_level"),
                        ),
                        has_whatsapp="add_on_whatsapp" in badges,
                        has_chat="add_on_chat" in badges,
                        url=f"{self.BASE_URL}{item.get('post_url')}",
                        description=item.get("masked_description"),
                        image_count=int(item.get("image_count") or 0),
                    )
                )
            return clean_results
        except Exception:
            return []


if __name__ == "__main__":
    client = OpenSooqClient()
    print("Testing OpenSooq Saudi Arabia Search ('ايفون' / iPhones)...")
    results = client.search(query="ايفون")
    print(f"[+] Retrieved {len(results)} structured listings directly from Next.js SSR!\n")
    for r in results[:3]:
        print(f" * [{r.price_raw or 'N/A'}] {r.title}")
        print(f"   Category: {r.category} | Location: {r.city} - {r.neighborhood or ''}")
        print(f"   Seller: {r.seller.name} (Rating: {r.seller.rating}/5) | WhatsApp: {'Yes' if r.has_whatsapp else 'No'}")
        print(f"   URL: {r.url}\n")
