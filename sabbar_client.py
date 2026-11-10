"""
Sabbar Gig & Jobs Private Client (Typed Python 3.11+)
Reverse-engineered from Sabbar's structured schema and SSR stream (sabbar.com).
Extracts active Saudi operational, retail, tech, and gig jobs with verified salaries, company names, and descriptions.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import httpx
import re
import json


@dataclass
class SabbarJobItem:
    id: str
    title: str
    company_name: Optional[str]
    salary_text: Optional[str]
    location: str
    description: str
    job_url: str


class SabbarClient:
    """Production client for Sabbar Jobs & Gigs Platform."""
    BASE_URL = "https://sabbar.com"

    def __init__(self, timeout: float = 12.0):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept-Language": "ar,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        self.client = httpx.Client(headers=self.headers, follow_redirects=True, timeout=timeout)

    def list_jobs(self, filter_slug: str = "") -> List[SabbarJobItem]:
        """
        Fetch active jobs from Sabbar.
        Optional filter_slug:
         - 'm-الخدمات-اللوجستية-والمستودعات' (Logistics & Warehouses)
         - 't-دوام-جزئي-w-نسائية' (Part-time Female Jobs)
         - 'm-ضيافة-ومطاعم' (Hospitality & Restaurants)
        """
        url = f"{self.BASE_URL}/ar/jobs"
        if filter_slug:
            url = f"{url}/{filter_slug}"

        resp = self.client.get(url)
        if resp.status_code != 200:
            return []

        results = []
        json_lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', resp.text, flags=re.DOTALL)
        for j in json_lds:
            try:
                data = json.loads(j)
                if isinstance(data, dict) and data.get("@type") == "ItemList":
                    for item in data.get("itemListElement", []):
                        raw_name = item.get("name", "")
                        # Parse salary if present: "الراتب ريال 2000 شهرياً"
                        sal_m = re.search(r'الراتب\s*(?:ريال)?\s*([0-9,]+)\s*(?:ريال)?\s*(شهرياً)?', raw_name)
                        salary_text = sal_m.group(0) if sal_m else None

                        # Parse company: "مطلوب ... في <company> السعودية"
                        comp_m = re.search(r'في\s+(.*?)\s+(?:السعودية|-)', raw_name)
                        company = comp_m.group(1).strip() if comp_m else None

                        # Parse role title
                        title_m = re.search(r'مطلوب\s+(.*?)\s+في', raw_name)
                        title = title_m.group(1).strip() if title_m else raw_name

                        url_path = item.get("url", "")
                        job_id_m = re.search(r'id-([a-f0-9-]+)', url_path)
                        job_id = job_id_m.group(1) if job_id_m else url_path

                        results.append(
                            SabbarJobItem(
                                id=job_id,
                                title=title,
                                company_name=company,
                                salary_text=salary_text,
                                location="Saudi Arabia (KSA)",
                                description=item.get("description", "").strip(),
                                job_url=f"{self.BASE_URL}{url_path}" if url_path.startswith("/") else url_path,
                            )
                        )
            except Exception:
                continue
        return results


if __name__ == "__main__":
    client = SabbarClient()
    print("Testing Sabbar Jobs Client...")
    jobs = client.list_jobs()
    print(f"[+] Retrieved {len(jobs)} active jobs from Sabbar:\n")
    for j in jobs[:5]:
        print(f" * [{j.id[:8]}...] {j.title}")
        print(f"   Company: {j.company_name or 'N/A'} | Salary: {j.salary_text or 'Disclosed upon interview'}")
        print(f"   URL: {j.job_url}")
        print(f"   Desc: {j.description[:90]}...\n")
