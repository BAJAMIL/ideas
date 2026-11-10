"""
Aqar Real Estate Private Client (Typed Python 3.11+)
Reverse-engineered from Aqar's Next.js streaming RSC layer (sa.aqar.fm).
Extracts verified real estate listings with official REGA prices, room counts, area, GPS coordinates, and neighborhood metadata.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import httpx
import re
import json


@dataclass
class AqarPropertyItem:
    id: int
    title: str
    price: int
    area_sqm: Optional[int]
    beds: Optional[int]
    bathrooms: Optional[int]
    living_rooms: Optional[int]
    city: str
    district: str
    address: str
    latitude: Optional[float]
    longitude: Optional[float]
    rnpl_monthly_installment: Optional[int]
    rent_period_text: Optional[str]
    apartment_type: Optional[str]
    description: str
    property_url: str
    images: List[str]
    advertiser_name: Optional[str]


class AqarClient:
    """Production client for Aqar Real Estate Marketplace."""
    BASE_URL = "https://sa.aqar.fm"

    def __init__(self, timeout: float = 15.0):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept-Language": "ar,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        self.client = httpx.Client(headers=self.headers, follow_redirects=True, timeout=timeout)

    def _extract_array(self, text: str, marker: str) -> List[Dict[str, Any]]:
        results = []
        idx = text.find(marker)
        while idx != -1:
            start_arr = text.find('[', idx)
            if start_arr == -1:
                break
            depth = 0
            end_arr = -1
            for i in range(start_arr, len(text)):
                if text[i] == '[':
                    depth += 1
                elif text[i] == ']':
                    depth -= 1
                    if depth == 0:
                        end_arr = i + 1
                        break
            if end_arr != -1:
                arr_str = text[start_arr:end_arr]
                try:
                    arr = json.loads(arr_str)
                    if isinstance(arr, list):
                        results.extend(arr)
                except Exception:
                    pass
            idx = text.find(marker, idx + 1)
        return results

    def search_properties(self, category: str = "شقق-للإيجار", city: str = "الرياض") -> List[AqarPropertyItem]:
        """
        Query properties by category and city.
        Common categories:
         - 'شقق-للإيجار' (Apartments for Rent)
         - 'فلل-للبيع' (Villas for Sale)
         - 'أراضي-للبيع' (Land for Sale)
         - 'عقارات-تجارية' (Commercial)
        """
        url = f"{self.BASE_URL}/{category}/{city}"
        resp = self.client.get(url)
        if resp.status_code != 200:
            return []

        chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', resp.text)
        all_raw = []
        for chunk in chunks:
            if 'sov_listings' in chunk or '"listings":' in chunk:
                unescaped = chunk.replace(r'\"', '"').replace(r'\\', '\\')
                all_raw.extend(self._extract_array(unescaped, '"sov_listings":'))
                all_raw.extend(self._extract_array(unescaped, '"listings":'))

        seen_ids = set()
        items = []
        for raw in all_raw:
            pid = raw.get("id")
            if not pid or pid in seen_ids:
                continue
            seen_ids.add(pid)

            loc = raw.get("location") or {}
            user = raw.get("user") or {}
            raw_imgs = raw.get("imgs") or []
            images = [f"https://images.aqar.fm/{img}" for img in raw_imgs if img]

            items.append(
                AqarPropertyItem(
                    id=pid,
                    title=raw.get("title", f"Property #{pid}"),
                    price=int(raw.get("price") or raw.get("rega_total_price") or 0),
                    area_sqm=raw.get("area"),
                    beds=raw.get("beds"),
                    bathrooms=raw.get("wc"),
                    living_rooms=raw.get("livings"),
                    city=raw.get("city", city),
                    district=raw.get("district", ""),
                    address=raw.get("address", ""),
                    latitude=loc.get("lat"),
                    longitude=loc.get("lng"),
                    rnpl_monthly_installment=raw.get("rnpl_monthly_price"),
                    rent_period_text=raw.get("rent_period_text"),
                    apartment_type=raw.get("apartment_type"),
                    description=raw.get("content", ""),
                    property_url=f"{self.BASE_URL}{raw.get('path', '')}",
                    images=images,
                    advertiser_name=user.get("name"),
                )
            )
        return items


if __name__ == "__main__":
    client = AqarClient()
    print("Testing Aqar Real Estate Client ('شقق-للإيجار/الرياض')...")
    props = client.search_properties("شقق-للإيجار", "الرياض")
    print(f"[+] Retrieved {len(props)} structured real estate properties from Aqar RSC stream:\n")
    for p in props[:5]:
        print(f" * [{p.id}] {p.title}")
        print(f"   Price: {p.price:,} SAR | Installment: {p.rnpl_monthly_installment or 'N/A'} SAR/mo ({p.rent_period_text or 'Annual'})")
        print(f"   Specs: {p.area_sqm or '?'} m² | {p.beds or '?'} beds | {p.bathrooms or '?'} baths | {p.living_rooms or '?'} majlis")
        print(f"   Location: {p.city} - {p.district} (GPS: {p.latitude}, {p.longitude})")
        print(f"   Advertiser: {p.advertiser_name or 'Direct Owner/Broker'} | URL: {p.property_url}\n")
