"""
Unified Saudi & Regional Marketplace Intelligence Registry
Provides a unified API to query all reverse-engineered Saudi platforms:
  1. Haraj (Consumer & Electronics Classifieds)
  2. OpenSooq (General Classifieds & Direct Contact)
  3. Salla App Store (Merchant Apps & E-Commerce Micro-SaaS)
  4. Aqar (Real Estate & Housing Rental/Sale)
  5. Syarah (Automotive & Financing)
  6. Sabbar (Hourly, Operational & Retail Jobs)
"""

from typing import Dict, Any, List
import time
from haraj_client import HarajClient
from opensooq_client import OpenSooqClient
from salla_client import SallaMarketplaceClient
from aqar_client import AqarClient
from syarah_client import SyarahClient
from sabbar_client import SabbarClient


class MarketplaceRegistry:
    """Central gateway for all reverse-engineered platforms."""

    def __init__(self):
        self.haraj = HarajClient()
        self.opensooq = OpenSooqClient()
        self.salla = SallaMarketplaceClient()
        self.aqar = AqarClient()
        self.syarah = SyarahClient()
        self.sabbar = SabbarClient()

    def run_health_check(self) -> Dict[str, Any]:
        """Test live connectivity and data extraction across all 6 targets."""
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

        # 4. Aqar
        t0 = time.time()
        try:
            props = self.aqar.search_properties("شقق-للإيجار", "الرياض")
            report["Aqar (Real Estate)"] = {
                "status": "ONLINE" if props else "RESTRICTED (Cloudflare 403 on cloud IP)",
                "items_count": len(props),
                "latency_sec": round(time.time() - t0, 2),
                "sample": f"{props[0].title} ({props[0].price:,} SAR)" if props else "Requires residential IP/residential proxy"
            }
        except Exception as e:
            report["Aqar (Real Estate)"] = {"status": "ERROR", "error": str(e)}

        # 5. Syarah
        t0 = time.time()
        try:
            cars = self.syarah.get_inventory()
            sample_str = None
            if cars:
                c0 = cars[0]
                t_val = c0.get("title") if isinstance(c0, dict) else getattr(c0, "title", "Car")
                p_val = c0.get("selling_price") if isinstance(c0, dict) else getattr(c0, "selling_price", "N/A")
                sample_str = f"{t_val} ({p_val or 'N/A'} SAR)"
            report["Syarah (Cars)"] = {
                "status": "ONLINE",
                "items_count": len(cars),
                "latency_sec": round(time.time() - t0, 2),
                "sample": sample_str
            }
        except Exception as e:
            report["Syarah (Cars)"] = {"status": "ERROR", "error": str(e)}

        # 6. Sabbar
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

        return report

    def collect_all_signals(self) -> str:
        """Aggregates high-value market signals from all connected Saudi platforms for agent analysis."""
        sections = []

        # 1. Haraj
        try:
            from haraj_client import fetch_haraj_consumer_signals
            sections.append(fetch_haraj_consumer_signals(limit_per_cat=2))
        except Exception as e:
            sections.append(f"### Haraj Market Signals:\n- [ERROR] {e}")

        # 2. Salla App Store
        try:
            apps = self.salla.list_apps(limit=8)
            salla_lines = ["### Salla App Store Merchant Demands & Micro-SaaS Pricing:"]
            for a in apps:
                price = f"{a.plan.price} {a.plan.suffix or 'SAR'}" if a.plan else "Free"
                rating = f"★ {a.rating.average:.1f}" if a.rating and a.rating.average else ""
                salla_lines.append(f"- [MERCHANT_SAAS] **{a.name}** ({price}) {rating} | Category: {a.category_name or 'E-Commerce'} | {a.tagline or ''}")
            sections.append("\n".join(salla_lines))
        except Exception as e:
            sections.append(f"### Salla App Store:\n- [ERROR] {e}")

        # 3. OpenSooq
        try:
            os_items = self.opensooq.search(query="ايفون", limit=5)
            os_lines = ["### OpenSooq Saudi Consumer Secondary Market Prices:"]
            for item in os_items:
                price = f"{item.price:,} SAR" if item.price else "On Negotiation"
                loc = f"{item.city} ({item.neighborhood})" if item.neighborhood else item.city
                os_lines.append(f"- [CONSUMER_LISTING] [{item.title}]({item.url}) | Price: {price} | Loc: {loc}")
            sections.append("\n".join(os_lines))
        except Exception as e:
            sections.append(f"### OpenSooq:\n- [ERROR] {e}")

        # 4. Syarah
        try:
            cars = self.syarah.get_inventory()[:5]
            syarah_lines = ["### Syarah Saudi Automotive Inventory & Financing:"]
            for c in cars:
                t = c.get("title") if isinstance(c, dict) else getattr(c, "title", "Car")
                p = c.get("selling_price") if isinstance(c, dict) else getattr(c, "selling_price", "N/A")
                syarah_lines.append(f"- [AUTO_MARKET] {t} | Price: {p} SAR")
            sections.append("\n".join(syarah_lines))
        except Exception as e:
            sections.append(f"### Syarah:\n- [ERROR] {e}")

        # 5. Sabbar
        try:
            jobs = self.sabbar.list_jobs()[:5]
            sabbar_lines = ["### Sabbar Saudi Operational Hiring & Salaries:"]
            for j in jobs:
                sal = f"{j.salary} SAR" if j.salary else "Competitive"
                sabbar_lines.append(f"- [HIRING_SIGNAL] **{j.title}** ({j.company_name or 'Saudi Retail/F&B'}) | Loc: {j.city or 'KSA'} | Salary: {sal}")
            sections.append("\n".join(sabbar_lines))
        except Exception as e:
            sections.append(f"### Sabbar:\n- [ERROR] {e}")

        return "\n\n".join(sections)


if __name__ == "__main__":
    registry = MarketplaceRegistry()
    print("=" * 70)
    print("🇸🇦 SAUDI & REGIONAL MARKETPLACE INTELLIGENCE HEALTH CHECK")
    print("=" * 70)
    results = registry.run_health_check()
    for name, stats in results.items():
        status_icon = "✅" if stats.get("status") == "ONLINE" else "❌"
        print(f"{status_icon} [{stats.get('status')}] {name}")
        if stats.get("status") == "ONLINE":
            print(f"    - Extracted Items: {stats.get('items_count')}")
            print(f"    - Latency: {stats.get('latency_sec')}s")
            print(f"    - Live Sample: {stats.get('sample')}")
        else:
            print(f"    - Error: {stats.get('error')}")
        print("-" * 70)
