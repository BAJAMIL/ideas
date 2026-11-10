"""
Kafiil Micro-Services & Freelance Projects Client (Typed Python 3.11+)
Reverse-engineered from Kafiil (https://kafiil.com).
Extracts active software services, digital templates, and verified client paid requests.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import httpx
import re

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


@dataclass
class KafiilItem:
    id: str
    title: str
    item_type: str  # 'service' or 'project'
    url: str
    price_or_budget: Optional[str] = None
    category: Optional[str] = None
    proposals_or_sales: Optional[int] = None


class KafiilClient:
    """Production client for Kafiil Services & Freelance Projects."""
    BASE_URL = "https://kafiil.com"

    def __init__(self, timeout: float = 15.0):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept-Language": "ar,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        self.client = httpx.Client(headers=self.headers, follow_redirects=True, timeout=timeout)

    def get_services(self, category: str = "software") -> List[KafiilItem]:
        """Fetch digital products, software scripts, and pre-built templates."""
        url = f"{self.BASE_URL}/services/{category}" if category else f"{self.BASE_URL}/services"
        resp = self.client.get(url)
        if resp.status_code != 200:
            return []

        items = []
        seen = set()

        if BeautifulSoup:
            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.find_all("a", href=re.compile(r"/service/(\d+)"))
            for a in links:
                href = a.get("href", "")
                m = re.search(r"/service/(\d+)", href)
                if not m:
                    continue
                item_id = m.group(1)
                if item_id in seen:
                    continue
                title = a.get_text(strip=True)
                if not title or len(title) < 5:
                    continue
                seen.add(item_id)
                items.append(
                    KafiilItem(
                        id=item_id,
                        title=title,
                        item_type="service",
                        url=href if href.startswith("http") else f"{self.BASE_URL}{href}",
                        category=category,
                    )
                )
        else:
            matches = re.findall(r'<a[^>]+href="([^"]*?/service/(\d+)[^"]*?)"[^>]*>(.*?)</a>', resp.text, re.DOTALL)
            for href, item_id, raw_title in matches:
                if item_id in seen:
                    continue
                clean_title = re.sub(r'<[^>]+>', '', raw_title).strip()
                if not clean_title or len(clean_title) < 5:
                    continue
                seen.add(item_id)
                items.append(
                    KafiilItem(
                        id=item_id,
                        title=clean_title,
                        item_type="service",
                        url=href if href.startswith("http") else f"{self.BASE_URL}{href}",
                        category=category,
                    )
                )
        return items

    def get_projects(self) -> List[KafiilItem]:
        """Fetch real-time client paid freelance and software project briefs."""
        url = f"{self.BASE_URL}/projects"
        resp = self.client.get(url)
        if resp.status_code != 200:
            return []

        items = []
        seen = set()

        if BeautifulSoup:
            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.find_all("a", href=re.compile(r"/project/(\d+)"))
            for a in links:
                href = a.get("href", "")
                m = re.search(r"/project/(\d+)", href)
                if not m:
                    continue
                item_id = m.group(1)
                if item_id in seen:
                    continue
                title = a.get_text(strip=True)
                clean_title = re.sub(r'^(مفتوح|مكتمل|قيد التنفيذ)\s*', '', title)
                if not clean_title or len(clean_title) < 5:
                    continue
                seen.add(item_id)
                items.append(
                    KafiilItem(
                        id=item_id,
                        title=clean_title,
                        item_type="project",
                        url=href if href.startswith("http") else f"{self.BASE_URL}{href}",
                    )
                )
        else:
            matches = re.findall(r'<a[^>]+href="([^"]*?/project/(\d+)[^"]*?)"[^>]*>(.*?)</a>', resp.text, re.DOTALL)
            for href, item_id, raw_title in matches:
                if item_id in seen:
                    continue
                clean_title = re.sub(r'<[^>]+>', '', raw_title).strip()
                clean_title = re.sub(r'^(مفتوح|مكتمل|قيد التنفيذ)\s*', '', clean_title)
                if not clean_title or len(clean_title) < 5:
                    continue
                seen.add(item_id)
                items.append(
                    KafiilItem(
                        id=item_id,
                        title=clean_title,
                        item_type="project",
                        url=href if href.startswith("http") else f"{self.BASE_URL}{href}",
                    )
                )
        return items


if __name__ == "__main__":
    client = KafiilClient()
    print("Testing Kafiil Client...")
    services = client.get_services("software")
    print(f"[+] Loaded {len(services)} software products/templates:")
    for s in services[:3]:
        print(f" * [{s.id}] {s.title} ({s.url})")

    projects = client.get_projects()
    print(f"\n[+] Loaded {len(projects)} client paid project requests:")
    for p in projects[:3]:
        print(f" * [{p.id}] {p.title} ({p.url})")
