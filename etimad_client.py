import httpx
import json
import time
from typing import List, Dict, Any, Optional

class EtimadClient:
    """
    Reverse-engineered Client for Etimad (tenders.etimad.sa).
    Provides structured, programmatic access to 290,000+ Saudi government tenders,
    ministry procurement requests, submission deadlines, and RFP document costs.
    100% Free, zero headless browser required.
    """
    BASE_URL = "https://tenders.etimad.sa"
    ASYNC_ENDPOINT = "https://tenders.etimad.sa/Tender/AllSupplierTendersForVisitorAsync"

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'ar,en;q=0.9',
            'X-Requested-With': 'XMLHttpRequest',
        }
        self.session = httpx.Client(headers=self.headers, follow_redirects=True, timeout=20.0)
        self._init_session()

    def _init_session(self):
        """Establishes initial session to obtain required ASP.NET anti-forgery cookies."""
        try:
            self.session.get(f"{self.BASE_URL}/Tender/AllTendersForVisitor")
        except Exception as e:
            print(f"[Warn] Etimad session init: {e}")

    def get_tenders(
        self,
        page_index: int = 1,
        page_size: int = 10,
        tender_name: Optional[str] = None,
        agency_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch paginated government tenders.
        """
        params = {
            'PageIndex': page_index,
            'PageSize': page_size,
        }
        if tender_name:
            params['TenderName'] = tender_name
        if agency_name:
            params['AgencyName'] = agency_name

        resp = self.session.get(self.ASYNC_ENDPOINT, params=params)
        if resp.status_code != 200:
            return {'total_records': 0, 'tenders': []}

        try:
            data = resp.json()
            raw_items = data.get('data', [])
            total_records = data.get('totalCount') or data.get('recordsTotal', 0)

            clean_tenders = []
            for t in raw_items:
                clean_tenders.append({
                    'id': t.get('tenderId'),
                    'ref_number': t.get('referenceNumber'),
                    'title': t.get('tenderName', '').strip(),
                    'government_agency': t.get('agencyName', '').strip(),
                    'branch_department': t.get('branchName', '').strip(),
                    'type': t.get('tenderTypeName', '').strip(),
                    'activity': t.get('tenderActivityName', '').strip(),
                    'document_cost_sar': t.get('invitationCost', 0.0),
                    'submission_deadline': t.get('lastOfferPresentationDate'),
                    'submission_deadline_hijri': t.get('lastOfferPresentationDateHijri'),
                    'remaining_days': t.get('remainingDays'),
                    'remaining_hours': t.get('remainingHours'),
                    'url': f"{self.BASE_URL}/Tender/DetailsForVisitor?STenderId={t.get('tenderIdString')}"
                })

            return {
                'total_records': total_records,
                'page': page_index,
                'page_size': page_size,
                'tenders': clean_tenders
            }
        except Exception:
            return {'total_records': 0, 'tenders': []}

if __name__ == "__main__":
    client = EtimadClient()
    print("Fetching live government tenders from Etimad.sa...")
    res = client.get_tenders(page_index=1, page_size=5)
    print(f"Total Available Government Tenders in KSA: {res['total_records']:,}\n")

    for t in res['tenders']:
        print(f" * [Ref: {t['ref_number']}] {t['title']}")
        print(f"   Agency: {t['government_agency']} ({t['branch_department']})")
        print(f"   Type: {t['type']} | Activity: {t['activity']}")
        print(f"   RFP Document Cost: {t['document_cost_sar']} SAR | Remaining: {t['remaining_days']} days, {t['remaining_hours']} hrs")
        print(f"   Deadline: {t['submission_deadline']} ({t['submission_deadline_hijri']}H)")
        print(f"   URL: {t['url']}\n")
