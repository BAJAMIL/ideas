"""
Haraj Deep Reverse-Engineered Client
Extracts structured data directly from Haraj's React Router v7 Turbo-Stream SSR & JSON-LD engines.
Zero headless browser required, purely lightweight HTTP client.
"""

import httpx
import json
import re
from typing import Dict, Any, List, Optional

class HarajClient:
    BASE_URL = "https://haraj.com.sa"
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ar,en;q=0.9',
            'Cache-Control': 'no-cache',
        }
        self.client = httpx.Client(headers=self.headers, follow_redirects=True, timeout=20.0)

    def _decode_turbo_stream(self, html: str) -> Optional[Dict[str, Any]]:
        """Parses the React Router Turbo-Stream data embedded in the page."""
        idx = html.find('streamController.enqueue(')
        if idx == -1:
            return None
        
        start = idx + len('streamController.enqueue(')
        try:
            decoder = json.JSONDecoder()
            raw_str, _ = decoder.raw_decode(html[start:])
            stream_data = json.loads(raw_str)
        except Exception:
            return None

        # Resolve index references
        def resolve(val, visited=None):
            if visited is None:
                visited = set()
            if isinstance(val, int):
                if val in visited:
                    return f"<cycle_{val}>"
                if 0 <= val < len(stream_data):
                    visited.add(val)
                    return resolve(stream_data[val], visited.copy())
                return val
            elif isinstance(val, dict):
                res = {}
                for k, v in val.items():
                    if k.startswith('_') and k[1:].lstrip('-').isdigit():
                        idx_k = int(k[1:])
                        k_name = str(stream_data[idx_k]) if 0 <= idx_k < len(stream_data) else k
                    else:
                        k_name = k
                    res[k_name] = resolve(v, visited.copy())
                return res
            elif isinstance(val, list):
                return [resolve(x, visited.copy()) for x in val]
            return val

        return resolve(stream_data[0])

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search listings by keyword, returning fully decoded rich post objects."""
        url = f"{self.BASE_URL}/search/{query}/"
        resp = self.client.get(url)
        if resp.status_code != 200:
            return []
        
        resolved = self._decode_turbo_stream(resp.text)
        if resolved and 'loaderData' in resolved:
            loader = resolved['loaderData']
            search_loader = loader.get('en:search-keyword') or loader.get('en:search-layout')
            if search_loader and 'posts' in search_loader and isinstance(search_loader['posts'], list):
                return search_loader['posts']
        
        # Fallback to JSON-LD
        m_jsonld = re.search(r'<script[^>]*id="json-ld-search-results"[^>]*>(.*?)</script>', resp.text, re.DOTALL)
        if m_jsonld:
            try:
                data = json.loads(m_jsonld.group(1))
                items = data.get('itemListElement', [])
                return [it.get('item', {}) for it in items]
            except Exception:
                pass
        return []

    def get_post(self, post_id: str | int) -> Optional[Dict[str, Any]]:
        """Fetch a specific listing by its ad ID."""
        url = f"{self.BASE_URL}/{post_id}/"
        resp = self.client.get(url)
        if resp.status_code != 200:
            return None
        
        # Extract Schema.org details
        m_post = re.search(r'<script[^>]*id="json-ld-post-details"[^>]*>(.*?)</script>', resp.text, re.DOTALL)
        post_details = json.loads(m_post.group(1)) if m_post else {}
        
        # Extract Breadcrumbs
        m_crumbs = re.search(r'<script[^>]*id="breadcrumb_list_json_ld"[^>]*>(.*?)</script>', resp.text, re.DOTALL)
        crumbs = json.loads(m_crumbs.group(1)) if m_crumbs else {}
        
        # Extract rich turbo-stream state
        resolved = self._decode_turbo_stream(resp.text)
        rich_post = None
        if resolved and 'loaderData' in resolved:
            catchall = resolved['loaderData'].get('en:catchall', {})
            queries = catchall.get('dehydratedState', {}).get('queries', [])
            for q in queries:
                if q.get('queryKey', [None])[0] == 'FetchAds':
                    posts = q.get('state', {}).get('data', {}).get('items', [])
                    if posts:
                        rich_post = posts[0]
                        break
        
        return {
            'json_ld': post_details,
            'breadcrumbs': crumbs.get('itemListElement', []),
            'rich_data': rich_post
        }

    def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Fetch seller profile and all active ads posted by them."""
        url = f"{self.BASE_URL}/users/{username}/"
        resp = self.client.get(url)
        if resp.status_code != 200:
            return {'user': None, 'posts': []}
        
        resolved = self._decode_turbo_stream(resp.text)
        if not resolved or 'loaderData' not in resolved:
            return {'user': None, 'posts': []}
        
        user_prof = resolved['loaderData'].get('en:user-profile', {})
        return {
            'user': user_prof.get('user'),
            'posts': user_prof.get('posts', [])
        }


if __name__ == "__main__":
    client = HarajClient()
    print("1. Testing Search ('RTX 3060')...")
    results = client.search("RTX 3060")
    print(f"   Found {len(results)} rich listings!")
    if results:
        p = results[0]
        print(f"   Sample: [{p.get('id')}] {p.get('title')}")
        print(f"   Author: {p.get('authorUsername')} (ID: {p.get('authorId')})")
        print(f"   Location: {p.get('city')} - {p.get('geoNeighborhood')} (GeoHash: {p.get('geoHash')})")
        print(f"   Price: {p.get('price', {}).get('formattedPrice')} SAR")
        print(f"   Tags: {p.get('tags')}")

    print("\n2. Testing Single Post Fetch ('11192403349')...")
    post_info = client.get_post("11192403349")
    if post_info:
        print(f"   Title: {post_info['json_ld'].get('name')}")
        print(f"   Price: {post_info['json_ld'].get('offers', {}).get('price')} SAR")
        print(f"   Crumbs: {[c.get('item', {}).get('name') for c in post_info['breadcrumbs']]}")

    print("\n3. Testing Seller Profile ('sultan4101')...")
    prof = client.get_user_profile("sultan4101")
    print(f"   Seller active ads: {len(prof['posts'])}")
    for ad in prof['posts']:
        print(f"    - {ad.get('title')} ({ad.get('city')})")
