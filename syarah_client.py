import httpx
import json
import re
from typing import List, Dict, Any, Optional

class SyarahClient:
    """
    Reverse-engineered Syarah.com Automotive Client.
    Extracts inspected and certified car inventory, cash/installment pricing,
    odometer, engine specs, and condition directly from the SSR payload.
    """
    BASE_URL = "https://syarah.com"

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept-Language': 'ar,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        self.client = httpx.Client(headers=self.headers, follow_redirects=True, timeout=20.0)

    def get_inventory(self, search_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch car inventory from Syarah catalog."""
        url = search_url or f"{self.BASE_URL}/autos"
        resp = self.client.get(url)
        if resp.status_code != 200:
            return []

        marker = 'window.FULL_PAGE_DATA = '
        idx = resp.text.find(marker)
        if idx == -1:
            return []

        try:
            start = idx + len(marker)
            decoder = json.JSONDecoder()
            data, _ = decoder.raw_decode(resp.text[start:])
            posts = data.get('posts', [])
            
            clean_cars = []
            for p in posts:
                g4 = p.get('g4_data_layer', {})
                clean_cars.append({
                    'id': p.get('id'),
                    'title': p.get('title', '').strip(),
                    'make': g4.get('post_make'),
                    'model': g4.get('post_model'),
                    'year': g4.get('post_year'),
                    'trim': g4.get('post_ext'),
                    'condition': g4.get('post_condition'),
                    'price_cash': g4.get('post_price') or p.get('sellingprice'),
                    'monthly_installment': p.get('monthly_installment'),
                    'mileage': g4.get('post_mileage'),
                    'transmission': g4.get('post_transmission'),
                    'fuel': g4.get('post_fuel'),
                    'city': g4.get('post_city'),
                    'exterior_color': g4.get('post_exterior_color_id'),
                    'interior_color': g4.get('post_interior_color_id'),
                    'engine_size': g4.get('post_engine_size'),
                    'is_inspected': p.get('warranty_tag', {}).get('tag_key') == 'inspected',
                    'url': f"{self.BASE_URL}{p.get('product_url')}",
                    'main_image': p.get('image_url'),
                })
            return clean_cars
        except Exception:
            return []

if __name__ == "__main__":
    client = SyarahClient()
    print("Testing Syarah Inventory Extraction (/autos)...")
    cars = client.get_inventory()
    print(f"Retrieved {len(cars)} certified vehicles directly from Syarah!\n")
    for c in cars[:5]:
        print(f" * [{c['price_cash']} SAR] (Installment: {c['monthly_installment']} SAR/mo)")
        print(f"   Vehicle: {c['make']} {c['model']} {c['trim']} ({c['year']})")
        print(f"   Specs: Odometer: {c['mileage']} km | {c['transmission']} | {c['fuel']} | {c['engine_size']}L")
        print(f"   Location: {c['city']} | Inspected: {'Yes' if c['is_inspected'] else 'No'}")
        print(f"   URL: {c['url']}\n")
