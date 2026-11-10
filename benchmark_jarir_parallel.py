"""
Jarir Extreme Parallel Extraction Benchmark (BAJAMIL Ideas)
Fires concurrent asynchronous requests across all major tech, gaming & retail categories on Jarir.
Demonstrates maximum throughput, latency, price distribution, and product discovery.
"""

import asyncio
import json
import time
from typing import Any, Dict, List
import httpx

INDEX_KEYS = {
    "en": "key_KcSYfmQTEwRpBnd9",
    "ar": "key_g0Gi7pKaE5cyqDGl",
}
API_BASE = "https://ac.cnstrc.com/search"

# High-yield category search targets across English and Arabic
TARGET_QUERIES = [
    # Computing & Laptops
    ("laptop", "en", "Laptops & MacBooks"),
    ("macbook", "en", "Apple Silicon MacBooks"),
    ("gaming laptop", "en", "Gaming Laptops"),
    # Phones & Tablets
    ("iphone", "en", "iPhones & Apple Devices"),
    ("samsung galaxy", "en", "Samsung Flagships"),
    ("ipad", "en", "iPads & Tablets"),
    # Gaming & PC Master Race
    ("rtx", "en", "NVIDIA RTX GPUs & Builds"),
    ("playstation 5", "en", "PS5 Consoles & Games"),
    ("gaming monitor", "en", "High-Refresh Monitors"),
    ("digital card", "en", "Digital Gift Cards"),
    # Arabic Localized High-Demand Tech
    ("بلايستيشن", "ar", "PlayStation Arabic Catalog"),
    ("لابتوب قيمنق", "ar", "Gaming Laptops Arabic"),
    ("سماعات ابل", "ar", "AirPods & Audio Arabic"),
    ("شاشة قيمنق", "ar", "Gaming Displays Arabic"),
    ("طابعة ليزر", "ar", "Laser Printers Arabic"),
]


async def fetch_category(
    client: httpx.AsyncClient,
    query: str,
    lang: str,
    category_label: str,
    limit: int = 50,
) -> Dict[str, Any]:
    key = INDEX_KEYS.get(lang, INDEX_KEYS["en"])
    url = f"{API_BASE}/{httpx.URL(query).raw_path.decode('utf-8')}"
    params = {
        "key": key,
        "num_results_per_page": limit,
    }

    t0 = time.time()
    try:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        latency = time.time() - t0
        data = resp.json().get("response", {})
        results = data.get("results", [])
        total = data.get("total_num_results", 0)

        products = []
        for r in results:
            item_data = r.get("data", {})
            metadata = item_data.get("metadata", {}) or {}
            raw_price = item_data.get("price") or metadata.get("price") or 0.0
            try:
                price_val = float(raw_price)
            except (ValueError, TypeError):
                price_val = 0.0

            sku = str(item_data.get("sku") or item_data.get("id") or "")
            products.append({
                "sku": sku,
                "title": r.get("value", ""),
                "price_sar": price_val,
                "brand": metadata.get("brand") or item_data.get("brand"),
                "model": metadata.get("model"),
                "url": f"https://www.jarir.com/sa-{lang}/{item_data.get('url')}" if item_data.get("url") else None,
                "image_cdn": f"https://ak-asset.jarir.com/akeneo-prod/asset/saas/{sku}.jpg",
            })

        return {
            "query": query,
            "lang": lang,
            "category": category_label,
            "latency_sec": round(latency, 3),
            "total_available": total,
            "extracted_count": len(products),
            "products": products,
        }
    except Exception as e:
        return {
            "query": query,
            "lang": lang,
            "category": category_label,
            "latency_sec": round(time.time() - t0, 3),
            "error": str(e),
            "total_available": 0,
            "extracted_count": 0,
            "products": [],
        }


async def run_parallel_benchmark():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    limits = httpx.Limits(max_keepalive_connections=20, max_connections=30)

    print("=" * 75)
    print("🚀 JARIR BOOKSTORE MAXIMUM ABILITY PARALLEL EXTRACTION BENCHMARK")
    print(f"Targeting {len(TARGET_QUERIES)} diverse categories simultaneously...")
    print("=" * 75)

    start_global = time.time()
    async with httpx.AsyncClient(headers=headers, limits=limits, timeout=12.0) as client:
        tasks = [
            fetch_category(client, q, lang, cat, limit=40)
            for q, lang, cat in TARGET_QUERIES
        ]
        results = await asyncio.gather(*tasks)

    total_time = time.time() - start_global
    print(f"\n[✓] ALL {len(results)} PARALLEL REQUESTS COMPLETED IN: {total_time:.2f} SECONDS!\n")

    # Aggregate metrics
    all_products = []
    total_catalog_available = 0

    print(f"{'Category':<32} | {'Lang':<4} | {'Latency':<8} | {'Found':<6} | {'Total in DB':<11}")
    print("-" * 75)
    for r in results:
        cat = r["category"]
        lang = r["lang"]
        lat = f"{r['latency_sec']}s"
        cnt = str(r["extracted_count"])
        tot = str(r["total_available"])
        total_catalog_available += r["total_available"]
        all_products.extend(r["products"])
        print(f"{cat:<32} | {lang:<4} | {lat:<8} | {cnt:<6} | {tot:<11}")

    print("-" * 75)
    print(f"Total Unique Products Extracted in Batch : {len(all_products):,}")
    print(f"Total Available Products in Searched DB   : {total_catalog_available:,}")
    print(f"Effective Throughput Rate                 : {len(all_products)/total_time:.1f} products/second")
    print(f"Network Latency per Parallel Query (Avg)  : {sum(r['latency_sec'] for r in results)/len(results):.3f}s")

    # Price Analytics
    prices = [p["price_sar"] for p in all_products if p["price_sar"] > 0]
    if prices:
        prices.sort()
        avg_price = sum(prices) / len(prices)
        min_p = prices[0]
        max_p = prices[-1]
        print("\n📊 PRICE DISTRIBUTION BENCHMARKS (SAR):")
        print(f" - Lowest Price Item    : {min_p:,.2f} SAR")
        print(f" - Highest Price Item   : {max_p:,.2f} SAR")
        print(f" - Average Tech Price   : {avg_price:,.2f} SAR")
        print(f" - Median Tech Price    : {prices[len(prices)//2]:,.2f} SAR")

    # Sample top 3 luxury items (highest SAR)
    top_items = sorted(all_products, key=lambda x: x["price_sar"], reverse=True)[:3]
    print("\n💎 TOP 3 HIGHEST VALUE HARDWARE EXTRACTED:")
    for i, it in enumerate(top_items, 1):
        print(f"  {i}. {it['title']}")
        print(f"     Price: {it['price_sar']:,.2f} SAR | Brand: {it['brand']} | SKU: {it['sku']}")
        print(f"     CDN Image: {it['image_cdn']}")

    # Export to JSON
    export_path = "jarir_parallel_dump.json"
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump({
            "benchmark_timestamp": time.time(),
            "duration_seconds": round(total_time, 2),
            "total_items_extracted": len(all_products),
            "categories_queried": [r["category"] for r in results],
            "products": all_products,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n[💾] Complete dataset saved to: {export_path}")


if __name__ == "__main__":
    asyncio.run(run_parallel_benchmark())
