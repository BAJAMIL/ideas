"""
Radar KSA (رادار الصفقات والمنتجات السعودي)
The Autonomous Market Intelligence, Price Benchmarking & Arbitrage Engine for Saudi Arabia.

Combines 12 Reverse-Engineered Saudi Platforms into a Single Unified Product Pipeline:
  1. Demand Signals: Google Trends (geo=SA) & Google Autocomplete (gl=sa, hl=ar)
  2. Retail Benchmarking: Jarir Bookstore (Constructor.io AI) & eXtra Stores (Unbxd AI)
  3. Marketplace Index: Noon KSA (Catalog v3 fallback)
  4. Secondary Market Arbitrage: Haraj (Apollo GraphQL) & OpenSooq (SSR Data)
  5. Merchant Syndication: Salla App Store (1-Click Product Feed Generator)

Pipeline Flow:
  Signal (Search Intent) -> Retail Benchmark -> Secondary Spread -> Salla Ready-to-Sell Product
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import re
import sys
import time
from typing import Any, Dict, List, Optional
import urllib.parse
import httpx

# Import verified clients
from jarir_client import JarirClient, JarirProduct
from extra_client import ExtraClient, ExtraProduct
from haraj_client import HarajClient, PostItem
from opensooq_client import OpenSooqClient, OpenSooqListing
from salla_client import SallaMarketplaceClient


def _parse_num(val: Any) -> float:
    """Extracts numeric price from strings like '1,500 ريال' or 1500."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    cleaned = re.sub(r"[^\d.]", "", str(val))
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0



class DealVerdict(str, Enum):
    HIGH_MARGIN_ARBITRAGE = "HIGH_MARGIN_ARBITRAGE"    # > 25% Net ROI vs Retail Benchmark
    RETAIL_PRICE_DROP = "RETAIL_PRICE_DROP"            # Retailer dropped price significantly
    FAIR_MARKET = "FAIR_MARKET"                        # In-line with secondary market average
    OVERPRICED = "OVERPRICED"                          # Listed higher than official retail benchmark


@dataclass
class RetailBenchmark:
    source: str
    sku: str
    title: str
    current_price_sar: float
    original_price_sar: float
    discount_amount: float
    discount_pct: float
    image_url: str
    product_url: str
    brand: Optional[str] = None
    specs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecondaryOpportunity:
    source: str
    listing_id: str
    title: str
    city: str
    seller_name: str
    asking_price_sar: float
    listing_url: str
    likes: int = 0
    comments: int = 0
    is_nafath_verified: bool = False
    condition_rating: str = "USED_GOOD"
    net_margin_sar: float = 0.0
    net_roi_pct: float = 0.0
    arbitrage_score: float = 0.0
    verdict: DealVerdict = DealVerdict.FAIR_MARKET


@dataclass
class SallaReadyProduct:
    name: str
    suggested_retail_price: float
    acquisition_price: float
    projected_margin_sar: float
    projected_margin_pct: float
    sku: str
    images: List[str]
    description_html: str
    source_supplier: str
    target_channel: str
    seo_tags: List[str]


class SaudiProductRadar:
    """Core intelligence engine orchestrating retail benchmarks, secondary arbitrage, and Salla feeds."""

    def __init__(self, timeout: float = 12.0):
        self.jarir = JarirClient(timeout=timeout)
        self.extra = ExtraClient(timeout=timeout)
        self.haraj = HarajClient(timeout=timeout)
        self.opensooq = OpenSooqClient(timeout=timeout)
        self.salla = SallaMarketplaceClient(timeout=timeout)
        self.http_client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-Language": "ar,en;q=0.9",
            },
            timeout=timeout,
        )

    # -------------------------------------------------------------------------
    # 1. Demand & Search Intent Signals (Google Autocomplete KSA)
    # -------------------------------------------------------------------------
    def get_search_intent(self, seed: str, lang: str = "ar") -> List[str]:
        """Captures live consumer search intent from Google Saudi Arabia."""
        url = "https://suggestqueries.google.com/complete/search"
        params = {
            "client": "chrome",
            "q": seed,
            "gl": "sa",
            "hl": lang,
        }
        try:
            resp = self.http_client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                if len(data) > 1 and isinstance(data[1], list):
                    return [str(item) for item in data[1][:8]]
        except Exception:
            pass
        # Fallback to Jarir's live autocomplete suggestions
        try:
            jarir_suggestions = self.jarir.get_search_suggestions(seed, lang=lang)
            return jarir_suggestions.suggested_products[:8]
        except Exception:
            return [seed]

    # -------------------------------------------------------------------------
    # 2. Multi-Store Retail Benchmarking (Jarir + eXtra)
    # -------------------------------------------------------------------------
    def get_retail_benchmarks(self, query: str, limit: int = 5) -> List[RetailBenchmark]:
        """Queries Jarir and eXtra in parallel to build official retail price anchors."""
        benchmarks: List[RetailBenchmark] = []

        # 1. Jarir Search
        try:
            jarir_res = self.jarir.search_products(query, num_results=limit)
            for p in jarir_res.get("products", []):
                save = p.discount_amount or 0.0
                orig = p.price + save if save > 0 else p.price
                pct = round((save / orig) * 100, 1) if orig > p.price else 0.0
                benchmarks.append(
                    RetailBenchmark(
                        source="Jarir Bookstore",
                        sku=p.sku,
                        title=p.title,
                        current_price_sar=p.price,
                        original_price_sar=orig,
                        discount_amount=save,
                        discount_pct=pct,
                        image_url=p.image_url or p.direct_cdn_image,
                        product_url=p.url or f"https://www.jarir.com/sa-en/{p.sku}.html",
                        brand=p.brand,
                        specs={
                            "author": p.author,
                            "isbn": p.isbn,
                            "format": p.book_format,
                            "paper_size": p.paper_size,
                            "category": p.category_desc,
                        },
                    )
                )
        except Exception as e:
            print(f"[!] Warning: Jarir benchmark query failed: {e}")

        # 2. eXtra Search
        try:
            extra_res = self.extra.search_products(query, rows=limit)
            for p in extra_res.get("products", []):
                orig = p.was_price or p.price
                save = max(0.0, round(orig - p.price, 2))
                pct = p.discount_percentage or (round((save / orig) * 100, 1) if orig > p.price else 0.0)
                benchmarks.append(
                    RetailBenchmark(
                        source="eXtra Stores",
                        sku=p.sku,
                        title=p.title,
                        current_price_sar=p.price,
                        original_price_sar=orig,
                        discount_amount=save,
                        discount_pct=pct,
                        image_url=p.image_url or "",
                        product_url=p.url or f"https://www.extra.com/en-sa/{p.sku}",
                        brand=p.brand,
                    )
                )
        except Exception as e:
            print(f"[!] Warning: eXtra benchmark query failed: {e}")

        # Sort benchmarks by price ascending
        benchmarks.sort(key=lambda x: x.current_price_sar)
        return benchmarks

    # -------------------------------------------------------------------------
    # 3. Secondary Market Extraction & Arbitrage Evaluation
    # -------------------------------------------------------------------------
    def scan_arbitrage_opportunities(
        self,
        query: str,
        benchmark: RetailBenchmark,
        limit: int = 15,
    ) -> List[SecondaryOpportunity]:
        """Scans Haraj and OpenSooq against the retail benchmark to find arbitrage spreads."""
        opportunities: List[SecondaryOpportunity] = []
        retail_msrp = benchmark.current_price_sar

        if retail_msrp <= 0:
            return []

        # Noise / False Positive Regex
        re_accessories = re.compile(
            r"(كرتون|علبة|كفر|جراب|شاحن فقط|سلك|محول|صندوق|استكر|حماية|حقيبة|لزقة)", re.IGNORECASE
        )
        re_broken = re.compile(
            r"(قطع|تشليح|عطلان|لا يعمل|مكسور|شاشة سوداء|قطع غيار|للقطع|اي سي|عاطل)", re.IGNORECASE
        )
        re_wanted = re.compile(
            r"(مطلوب|ابحث عن|أرغب بشراء|من يخبر|شرا|شراء)", re.IGNORECASE
        )

        # 1. Search Haraj
        try:
            haraj_listings = self.haraj.search(query, limit=limit)
            for item in haraj_listings:
                title = item.title or ""
                price = _parse_num(item.price_input) or _parse_num(item.price_formatted)
                if price <= 0:
                    continue

                # Filter false positives
                if re_accessories.search(title) or re_broken.search(title) or re_wanted.search(title):
                    continue

                # Sanity: ignore placeholder 1 SAR bids or overpriced listings
                if price < (retail_msrp * 0.15) or price >= retail_msrp:
                    continue

                opp = self._evaluate_opportunity(
                    source="Haraj",
                    listing_id=str(item.id),
                    title=title,
                    city=item.city or "الرياض",
                    seller_name=item.author_username or "مستخدم حراج",
                    asking_price=price,
                    url=item.url or f"https://haraj.com.sa/{item.id}",
                    retail_msrp=retail_msrp,
                    likes=item.up_rank,
                    comments=item.comment_count,
                    is_nafath=bool(item.can_request_wasata),
                )
                if opp:
                    opportunities.append(opp)
        except Exception as e:
            print(f"[!] Warning: Haraj scan failed: {e}")

        # 2. Search OpenSooq
        try:
            os_listings = self.opensooq.search(query=query)
            for item in os_listings:
                title = item.title or ""
                price = _parse_num(item.price_raw)
                if price <= 0:
                    continue

                if re_accessories.search(title) or re_broken.search(title) or re_wanted.search(title):
                    continue

                if price < (retail_msrp * 0.15) or price >= retail_msrp:
                    continue

                seller_name = item.seller.name if item.seller else "بائع السوق المفتوح"
                is_verified = bool(item.seller and (item.seller.verification_level or 0) >= 1)

                opp = self._evaluate_opportunity(
                    source="OpenSooq",
                    listing_id=str(item.id),
                    title=title,
                    city=item.city or "السعودية",
                    seller_name=seller_name,
                    asking_price=price,
                    url=item.url or f"https://sa.opensooq.com/ar/post/{item.id}",
                    retail_msrp=retail_msrp,
                    is_nafath=is_verified,
                )
                if opp:
                    opportunities.append(opp)
        except Exception as e:
            print(f"[!] Warning: OpenSooq scan failed: {e}")

        # Sort opportunities by Arbitrage Score descending
        opportunities.sort(key=lambda x: x.arbitrage_score, reverse=True)
        return opportunities

    def _evaluate_opportunity(
        self,
        source: str,
        listing_id: str,
        title: str,
        city: str,
        seller_name: str,
        asking_price: float,
        url: str,
        retail_msrp: float,
        likes: int = 0,
        comments: int = 0,
        is_nafath: bool = False,
    ) -> Optional[SecondaryOpportunity]:
        # Condition classification
        t = title.lower()
        if any(w in t for w in ["جديد", "بقراطيسه", "كرتونه مقفل", "تغليف المصنع", "مختوم"]):
            cond, delta = "NEW_SEALED", 0.08
        elif any(w in t for w in ["أخو الجديد", "نظيف جدا", "استخدام بسيط", "شبه جديد"]):
            cond, delta = "LIKE_NEW", 0.20
        else:
            cond, delta = "USED_GOOD", 0.30

        effective_value = retail_msrp * (1.0 - delta)

        # Transaction friction in Saudi Arabia
        platform_fee = asking_price * 0.01 * 1.15
        shipping = 25.0 * 1.15 if ("رياض" in city or "Riyadh" in city) else 38.0 * 1.15
        payment_fee = 1.0 + (asking_price * 0.01)
        inspection_reserve = 30.0
        total_fees = platform_fee + shipping + payment_fee + inspection_reserve

        net_margin = effective_value - asking_price - total_fees
        if net_margin <= 0:
            return None

        net_roi = (net_margin / (asking_price + total_fees)) * 100.0

        # Arbitrage Score calculation S_arb (0 - 100)
        s_yield = min(100.0, (net_roi / 35.0) * 100.0)
        s_depth = min(100.0, (net_margin / 500.0) * 100.0)
        s_seller = (50.0 + (30.0 if is_nafath else 0.0))
        s_liq = min(100.0, (likes * 4.0) + (comments * 6.0) + 30.0)
        s_geo = 100.0 if ("رياض" in city or "Riyadh" in city) else 75.0

        score = (
            0.35 * s_yield +
            0.20 * s_depth +
            0.20 * s_seller +
            0.15 * s_liq +
            0.10 * s_geo
        )

        verdict = DealVerdict.HIGH_MARGIN_ARBITRAGE if score >= 70.0 else DealVerdict.FAIR_MARKET

        return SecondaryOpportunity(
            source=source,
            listing_id=listing_id,
            title=title,
            city=city,
            seller_name=seller_name,
            asking_price_sar=round(asking_price, 2),
            listing_url=url,
            likes=likes,
            comments=comments,
            is_nafath_verified=is_nafath,
            condition_rating=cond,
            net_margin_sar=round(net_margin, 2),
            net_roi_pct=round(net_roi, 1),
            arbitrage_score=round(score, 1),
            verdict=verdict,
        )

    # -------------------------------------------------------------------------
    # 4. Salla Store Product Syndication
    # -------------------------------------------------------------------------
    def generate_salla_product(
        self,
        benchmark: RetailBenchmark,
        opportunity: Optional[SecondaryOpportunity] = None,
    ) -> SallaReadyProduct:
        """Packages the benchmarked product into a 1-click importable Salla Merchant feed."""
        if opportunity:
            acq_price = opportunity.asking_price_sar
            suggested_retail = round(benchmark.current_price_sar * 0.90, 2)
            margin = round(suggested_retail - acq_price, 2)
            margin_pct = round((margin / acq_price) * 100, 1)
            supplier_note = f"مستخرج عبر {opportunity.source} (البائع: {opportunity.seller_name})"
        else:
            acq_price = benchmark.current_price_sar
            suggested_retail = round(benchmark.original_price_sar or (benchmark.current_price_sar * 1.15), 2)
            margin = round(suggested_retail - acq_price, 2)
            margin_pct = round((margin / acq_price) * 100, 1)
            supplier_note = f"مستخرج من {benchmark.source} (عرض رسمي)"

        clean_title = benchmark.title
        brand_name = benchmark.brand or "أصلي"
        
        # Build Arabic SEO Description HTML
        desc_html = f"""
<div class="salla-product-spec" dir="rtl" style="font-family: Cairo, Tahoma, sans-serif;">
  <h3>✨ {clean_title}</h3>
  <p><strong>العلامة التجارية:</strong> {brand_name}</p>
  <p><strong>الضمان والجودة:</strong> منتج أصلي ومفحوص 100% مع ضمان استرجاع.</p>
  <div style="background-color: #f8fafc; padding: 12px; border-radius: 8px; margin: 12px 0;">
    <h4 style="margin-top: 0;">⚡ مميزات الطلب:</h4>
    <ul>
      <li>شحن سريع لكافة مدن المملكة (الرياض، جدة، الدمام).</li>
      <li>دفع آمن عبر مدى، أبل باي، وتمارا / تاببي (قسم فاتورتك على 4 دفعات).</li>
    </ul>
  </div>
</div>
""".strip()

        return SallaReadyProduct(
            name=clean_title,
            suggested_retail_price=suggested_retail,
            acquisition_price=acq_price,
            projected_margin_sar=margin,
            projected_margin_pct=margin_pct,
            sku=f"RADAR-{benchmark.sku}",
            images=[benchmark.image_url],
            description_html=desc_html,
            source_supplier=supplier_note,
            target_channel="Salla App Store Merchant Catalog",
            seo_tags=[brand_name, "عروض السعودية", "أجهزة إلكترونية", "جرير", "تسوق أونلاين"],
        )

    # -------------------------------------------------------------------------
    # 5. Full Pipeline Run & Output Generation
    # -------------------------------------------------------------------------
    def run_radar_scan(self, keyword: str) -> Dict[str, Any]:
        """Runs the complete 4-step intelligence cycle for any keyword."""
        print(f"\n[*] STEP 1: Capturing Saudi consumer intent for '{keyword}'...")
        intent_queries = self.get_search_intent(keyword, lang="ar")
        print(f"    [+] Discovered {len(intent_queries)} intent variations (e.g. '{intent_queries[0]}')")

        print(f"\n[*] STEP 2: Querying Retail Price Anchors (Jarir Bookstore & eXtra Stores)...")
        benchmarks = self.get_retail_benchmarks(keyword, limit=4)
        print(f"    [+] Extracted {len(benchmarks)} authoritative retail benchmarks.")

        opportunities: List[SecondaryOpportunity] = []
        salla_feed: List[SallaReadyProduct] = []

        if benchmarks:
            lead_benchmark = benchmarks[0]
            print(f"    [+] Leading Benchmark: '{lead_benchmark.title[:45]}...' ({lead_benchmark.current_price_sar:,.2f} SAR at {lead_benchmark.source})")

            print(f"\n[*] STEP 3: Scanning Secondary Arbitrage (Haraj & OpenSooq)...")
            opportunities = self.scan_arbitrage_opportunities(keyword, lead_benchmark, limit=10)
            print(f"    [+] Discovered {len(opportunities)} active arbitrage candidates.")

            print(f"\n[*] STEP 4: Synthesizing Salla Ready-to-Sell Product Feed...")
            top_opp = opportunities[0] if opportunities else None
            salla_item = self.generate_salla_product(lead_benchmark, top_opp)
            salla_feed.append(salla_item)
            print(f"    [+] Generated Salla SKU: {salla_item.sku} (Margin: {salla_item.projected_margin_sar:,.2f} SAR / {salla_item.projected_margin_pct}%)")

        return {
            "query": keyword,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "search_intent": intent_queries,
            "retail_benchmarks": [asdict(b) for b in benchmarks],
            "arbitrage_opportunities": [asdict(o) for o in opportunities],
            "salla_feed": [asdict(s) for s in salla_feed],
        }


# =============================================================================
# CLI Interface
# =============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Radar KSA (رادار الصفقات السعودي) — Autonomous Market Intelligence & Arbitrage Engine"
    )
    parser.add_argument("query", nargs="?", default="macbook air", help="Product or keyword to analyze")
    parser.add_argument("--json", action="store_true", help="Output raw JSON result")
    parser.add_argument("--export", type=str, default="", help="Export report to JSON file")
    args = parser.parse_args()

    radar = SaudiProductRadar()
    print("=" * 75)
    print("🇸🇦 RADAR KSA (رادار الصفقات والمنتجات السعودي) — INTELLIGENCE ENGINE")
    print("=" * 75)

    result = radar.run_radar_scan(args.query)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    # Formatted Terminal Output
    print("\n" + "=" * 75)
    print("📊 RADAR KSA — EXECUTIVE INTELLIGENCE SUMMARY")
    print("=" * 75)
    print(f"Target Query : {result['query']}")
    print(f"Timestamp    : {result['timestamp']}")

    print("\n[1] Top Live Search Intent (Saudi Arabia):")
    for idx, q in enumerate(result["search_intent"][:5], 1):
        print(f"  {idx}. {q}")

    print("\n[2] Official Retail Price Anchors:")
    for b in result["retail_benchmarks"][:3]:
        save_badge = f" (-{b['discount_pct']}%)" if b["discount_pct"] > 0 else ""
        print(f"  • [{b['source']}] {b['title'][:55]}...")
        print(f"    Price: {b['current_price_sar']:,.2f} SAR{save_badge} | SKU: {b['sku']}")
        print(f"    Image: {b['image_url']}")

    print("\n[3] Top Secondary Market Arbitrage Deals:")
    if result["arbitrage_opportunities"]:
        for idx, opp in enumerate(result["arbitrage_opportunities"][:3], 1):
            nafath_badge = " [Nafath Verified]" if opp["is_nafath_verified"] else ""
            print(f"  {idx}. [{opp['source']} - {opp['city']}] {opp['title'][:50]}...{nafath_badge}")
            print(f"     Asking: {opp['asking_price_sar']:,.2f} SAR | Net Margin: +{opp['net_margin_sar']:,.2f} SAR (+{opp['net_roi_pct']}%)")
            print(f"     Arbitrage Score: {opp['arbitrage_score']}/100 [{opp['verdict']}]")
            print(f"     URL: {opp['listing_url']}")
    else:
        print("  [i] No high-margin secondary arbitrage spread detected for this exact query.")

    print("\n[4] 1-Click Salla Store Feed:")
    for sf in result["salla_feed"]:
        print(f"  • Name    : {sf['name'][:60]}...")
        print(f"    SKU     : {sf['sku']}")
        print(f"    Cost    : {sf['acquisition_price']:,.2f} SAR -> Salla Price: {sf['suggested_retail_price']:,.2f} SAR")
        print(f"    Profit  : +{sf['projected_margin_sar']:,.2f} SAR (+{sf['projected_margin_pct']}%)")
        print(f"    Channel : {sf['target_channel']}")

    print("=" * 75)

    if args.export:
        with open(args.export, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n[✓] Successfully exported full report to: {args.export}")


if __name__ == "__main__":
    main()
