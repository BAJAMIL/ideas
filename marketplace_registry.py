"""
Unified Saudi & Regional Marketplace Intelligence Registry (12 Platforms)
Provides a unified API and live health check across all reverse-engineered platforms:
  1. Haraj (Consumer & Electronics Classifieds, Bids, Ratings)
  2. OpenSooq (Pan-Saudi Classifieds, WhatsApp Badges, Devices)
  3. Salla App Store (Merchant Apps & E-Commerce Micro-SaaS)
  4. Aqar (Real Estate & Housing Rental/Sale with REGA & GPS)
  5. Syarah (Automotive, Financing Installments, 200-Pt Inspection)
  6. Sabbar (Hourly, Operational & Retail Jobs)
  7. Jarir Bookstore (Tech, Gadgets, Books, Constructor.io AI Catalog)
  8. eXtra Stores (Consumer Electronics, Appliances, Discounts)
  9. Etimad (Saudi Government Tenders & Ministry Procurement RFPs)
  10. Kafiil (Arabic Freelance Projects, Micro-services & Templates)
  11. Nice One (Beauty, Skincare & Cosmetics E-Commerce)
  12. Golden Scent (Luxury Perfumes & Designer Fragrances)
"""

from typing import Dict, Any, List
import time
from signal_health import render_signals
from haraj_client import HarajClient
from opensooq_client import OpenSooqClient
from salla_client import SallaMarketplaceClient
from aqar_client import AqarClient
from syarah_client import SyarahClient
from sabbar_client import SabbarClient
from jarir_client import JarirClient
from extra_client import ExtraClient
from etimad_client import EtimadClient
from kafiil_client import KafiilClient
from niceone_client import NiceOneClient
from goldenscent_client import GoldenScentClient
from lulu_client import LuluClient


class MarketplaceRegistry:
    """Central gateway for all reverse-engineered platforms."""

    def __init__(self):
        self.haraj = HarajClient()
        self.opensooq = OpenSooqClient()
        self.salla = SallaMarketplaceClient()
        self.aqar = AqarClient()
        self.syarah = SyarahClient()
        self.sabbar = SabbarClient()
        self.jarir = JarirClient()
        self.extra = ExtraClient()
        self.etimad = EtimadClient()
        self.kafiil = KafiilClient()
        self.niceone = NiceOneClient()
        self.goldenscent = GoldenScentClient()
        self.lulu = LuluClient()

    def run_health_check(self) -> Dict[str, Any]:
        """Test live connectivity and data extraction across all platforms."""
        report = {}

        # 1. Haraj
        t0 = time.time()
        try:
            items = self.haraj.search("RTX", limit=3)
            report["Haraj"] = {
                "status": "ONLINE",
                "items_count": len(items),
                "latency_sec": round(time.time() - t0, 2),
                "sample": items[0].title if items else None
            }
        except Exception as e:
            report["Haraj"] = {"status": "ERROR", "error": str(e)}

        # 2. OpenSooq
        t0 = time.time()
        try:
            items = self.opensooq.search(query="ايفون")
            report["OpenSooq"] = {
                "status": "ONLINE",
                "items_count": len(items),
                "latency_sec": round(time.time() - t0, 2),
                "sample": items[0].title if items else None
            }
        except Exception as e:
            report["OpenSooq"] = {"status": "ERROR", "error": str(e)}

        # 3. Salla App Store
        t0 = time.time()
        try:
            apps = self.salla.list_apps(limit=3)
            report["Salla App Store"] = {
                "status": "ONLINE",
                "items_count": len(apps),
                "latency_sec": round(time.time() - t0, 2),
                "sample": f"{apps[0].name} ({apps[0].plan.price} {apps[0].plan.suffix or 'SAR'})" if apps else None
            }
        except Exception as e:
            report["Salla App Store"] = {"status": "ERROR", "error": str(e)}

        # 4. Aqar Real Estate
        t0 = time.time()
        try:
            props = self.aqar.search_properties("شقق-للإيجار", "الرياض")
            report["Aqar (Real Estate)"] = {
                "status": "ONLINE",
                "items_count": len(props),
                "latency_sec": round(time.time() - t0, 2),
                "sample": f"{props[0].title} ({props[0].price:,} SAR)" if props else None
            }
        except Exception as e:
            report["Aqar (Real Estate)"] = {"status": "ERROR", "error": str(e)}

        # 5. Syarah Cars
        t0 = time.time()
        try:
            cars = self.syarah.get_inventory()
            report["Syarah (Cars)"] = {
                "status": "ONLINE",
                "items_count": len(cars),
                "latency_sec": round(time.time() - t0, 2),
                "sample": f"{cars[0].get('make')} {cars[0].get('model')} ({cars[0].get('price_cash')} SAR)" if cars else None
            }
        except Exception as e:
            report["Syarah (Cars)"] = {"status": "ERROR", "error": str(e)}

        # 6. Sabbar Jobs
        t0 = time.time()
        try:
            jobs = self.sabbar.list_jobs()
            report["Sabbar (Gigs & Jobs)"] = {
                "status": "ONLINE",
                "items_count": len(jobs),
                "latency_sec": round(time.time() - t0, 2),
                "sample": f"{jobs[0].title} ({jobs[0].company_name or 'N/A'})" if jobs else None
            }
        except Exception as e:
            report["Sabbar (Gigs & Jobs)"] = {"status": "ERROR", "error": str(e)}

        # 7. Jarir Bookstore
        t0 = time.time()
        try:
            j_res = self.jarir.search_products("iphone", num_results=3)
            j_prods = j_res.get("products", [])
            report["Jarir Bookstore"] = {
                "status": "ONLINE",
                "items_count": len(j_prods),
                "latency_sec": round(time.time() - t0, 2),
                "sample": f"{j_prods[0].title} ({j_prods[0].price} SAR)" if j_prods else None
            }
        except Exception as e:
            report["Jarir Bookstore"] = {"status": "ERROR", "error": str(e)}

        # 8. eXtra Stores
        t0 = time.time()
        try:
            e_res = self.extra.search_products("iphone", rows=3)
            e_prods = e_res.get("products", [])
            report["eXtra Stores"] = {
                "status": "ONLINE",
                "items_count": len(e_prods),
                "latency_sec": round(time.time() - t0, 2),
                "sample": f"{e_prods[0].title} ({e_prods[0].price} SAR)" if e_prods else None
            }
        except Exception as e:
            report["eXtra Stores"] = {"status": "ERROR", "error": str(e)}

        # 9. Etimad Government Tenders
        t0 = time.time()
        try:
            et_res = self.etimad.get_tenders(page_size=3)
            tenders = et_res.get("tenders", [])
            report["Etimad Tenders"] = {
                "status": "ONLINE",
                "items_count": len(tenders),
                "latency_sec": round(time.time() - t0, 2),
                "sample": f"{tenders[0].get('name') or 'Tender'} ({tenders[0].get('agency') or 'Gov'})" if tenders else None
            }
        except Exception as e:
            report["Etimad Tenders"] = {"status": "ERROR", "error": str(e)}

        # 10. Kafiil
        t0 = time.time()
        try:
            k_projs = self.kafiil.get_projects()
            report["Kafiil (Services & Projects)"] = {
                "status": "ONLINE",
                "items_count": len(k_projs),
                "latency_sec": round(time.time() - t0, 2),
                "sample": k_projs[0].title if k_projs else None
            }
        except Exception as e:
            report["Kafiil (Services & Projects)"] = {"status": "ERROR", "error": str(e)}

        # 11. Nice One
        t0 = time.time()
        try:
            n_prods = self.niceone.search_products("عطر")
            report["Nice One (Beauty & Perfume)"] = {
                "status": "ONLINE",
                "items_count": len(n_prods),
                "latency_sec": round(time.time() - t0, 2),
                "sample": f"{n_prods[0].name} ({n_prods[0].price} SAR)" if n_prods else None
            }
        except Exception as e:
            report["Nice One (Beauty & Perfume)"] = {"status": "ERROR", "error": str(e)}

        # 12. Golden Scent
        t0 = time.time()
        try:
            g_prods = self.goldenscent.search_products("عطر")
            report["Golden Scent (Luxury Perfumes)"] = {
                "status": "ONLINE",
                "items_count": len(g_prods),
                "latency_sec": round(time.time() - t0, 2),
                "sample": f"{g_prods[0].name} ({g_prods[0].price} SAR)" if g_prods else None
            }
        except Exception as e:
            report["Golden Scent (Luxury Perfumes)"] = {"status": "ERROR", "error": str(e)}

        # 13. Lulu Hypermarket
        t0 = time.time()
        try:
            l_res = self.lulu.search_products("apple", page=1)
            l_prods = l_res.get("products", [])
            report["Lulu Hypermarket"] = {
                "status": "ONLINE",
                "items_count": len(l_prods),
                "latency_sec": round(time.time() - t0, 2),
                "sample": f"{l_prods[0].name} ({l_prods[0].price} SAR)" if l_prods else None
            }
        except Exception as e:
            report["Lulu Hypermarket"] = {"status": "ERROR", "error": str(e)}

        return report

    def collect_all_signals(self) -> str:
        """Renders live signals from all 12 platforms for the daily idea agent.

        run_health_check() already isolates each platform, so a single failure is
        reported as UNAVAILABLE rather than dropping the other eleven.
        """
        try:
            return render_signals(self.run_health_check())
        except Exception as exc:
            return (
                "### Unified Saudi marketplace signals (12 platforms)\n"
                f"- [UNAVAILABLE] all platforms: {exc}"
            )


if __name__ == "__main__":
    registry = MarketplaceRegistry()
    print("=" * 72)
    print("🇸🇦 SAUDI ARABIA & REGIONAL MARKETPLACE INTELLIGENCE SUITE (12 PLATFORMS)")
    print("=" * 72)
    results = registry.run_health_check()
    online_count = sum(1 for s in results.values() if s.get("status") == "ONLINE")
    for name, stats in results.items():
        status_icon = "✅" if stats.get("status") == "ONLINE" else "❌"
        print(f"{status_icon} [{stats.get('status')}] {name}")
        if stats.get("status") == "ONLINE":
            print(f"    - Extracted Items: {stats.get('items_count')}")
            print(f"    - Latency: {stats.get('latency_sec')}s")
            print(f"    - Live Sample: {stats.get('sample')}")
        else:
            print(f"    - Error: {stats.get('error')}")
        print("-" * 72)
    print(f"\nSummary: {online_count}/{len(results)} platforms operational.")
