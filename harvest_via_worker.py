"""
High-Speed Bulk Harvester via Local Cloudflare Worker Edge Proxy
Fires concurrent parallel queries through the running Cloudflare Worker at http://127.0.0.1:8787.
Extracts products from Jarir, eXtra, and Noon simultaneously with edge caching.
"""

import asyncio
import json
import time
from typing import Any, Dict, List
import httpx

WORKER_BASE = "http://127.0.0.1:8787"

SEARCH_TARGETS = [
    # Top Tech Flagships
    ("macbook pro", "en", "MacBook Pro M-Series"),
    ("iphone 16", "en", "Apple iPhone 16 Series"),
    ("samsung s24 ultra", "en", "Samsung Galaxy S24 Ultra"),
    ("ipad pro", "en", "Apple iPad Pro M-Chip"),
    # Gaming & PC Hardware
    ("rtx 4080", "en", "NVIDIA RTX 4080 / 5080 GPUs"),
    ("playstation 5 slim", "en", "PlayStation 5 Consoles"),
    ("nintendo switch oled", "en", "Nintendo Switch Handhelds"),
    ("gaming laptop asus", "en", "ASUS ROG Gaming Laptops"),
    ("gaming monitor 4k", "en", "4K High-Refresh Displays"),
    # Consumables & Lifestyle
    ("airpods pro", "en", "Apple AirPods & ANC Audio"),
    ("apple watch ultra", "en", "Smartwatches & Wearables"),
    ("espresso machine", "en", "Specialty Coffee Machines"),
    ("dji drone", "en", "Drones & Action Cameras"),
    # Arabic Queries (KSA Localized)
    ("بلايستيشن 5", "ar", "PlayStation Arabic Catalog"),
    ("لابتوب ابل", "ar", "Apple Laptops Arabic"),
    ("شاشة ذكية 65", "ar", "65-Inch Smart 4K TVs"),
    ("ماكينة اسبريسو", "ar", "Espresso Machines Arabic"),
    ("ساعة ذكية", "ar", "Smartwatches Arabic"),
]


async def query_worker_jarir(client: httpx.AsyncClient, query: str, lang: str, label: str) -> Dict[str, Any]:
    url = f"{WORKER_BASE}/api/jarir"
    t0 = time.time()
    try:
        resp = await client.get(url, params={"q": query, "lang": lang, "limit": 40}, timeout=10.0)
        latency = round(time.time() - t0, 3)
        cache_header = resp.headers.get("X-Edge-Cache", "UNKNOWN")
        data = resp.json()
        products = data.get("products", [])
        return {
            "source": "Jarir",
            "query": query,
            "label": label,
            "lang": lang,
            "status": resp.status_code,
            "cache": cache_header,
            "latency_sec": latency,
            "total_in_db": data.get("total", 0),
            "count": len(products),
            "products": products,
        }
    except Exception as e:
        return {
            "source": "Jarir",
            "query": query,
            "label": label,
            "lang": lang,
            "status": "ERROR",
            "error": str(e),
            "latency_sec": round(time.time() - t0, 3),
            "count": 0,
            "products": [],
        }


async def query_worker_compare(client: httpx.AsyncClient, query: str, lang: str, label: str) -> Dict[str, Any]:
    url = f"{WORKER_BASE}/api/compare"
    t0 = time.time()
    try:
        resp = await client.get(url, params={"q": query, "lang": lang}, timeout=15.0)
        latency = round(time.time() - t0, 3)
        data = resp.json()
        summary = data.get("summary", {})
        retailers = data.get("retailers", {})
        return {
            "query": query,
            "label": label,
            "latency_sec": latency,
            "worker_latency_ms": data.get("latency_ms", 0),
            "summary": summary,
            "retailers": retailers,
        }
    except Exception as e:
        return {
            "query": query,
            "label": label,
            "error": str(e),
            "latency_sec": round(time.time() - t0, 3),
        }


async def main():
    print("=" * 80)
    print("⚡ CLOUDFLARE WORKER HIGH-THROUGHPUT MULTI-STORE HARVESTER")
    print(f"Targeting {len(SEARCH_TARGETS)} categories in parallel through http://127.0.0.1:8787...")
    print("=" * 80)

    limits = httpx.Limits(max_keepalive_connections=30, max_connections=40)
    start_time = time.time()

    async with httpx.AsyncClient(limits=limits, timeout=15.0) as client:
        # Phase 1: Pure Jarir High-Speed Bulk Extraction through Worker
        print("\n[Phase 1] Extracting Jarir via Cloudflare Worker Edge Proxy...")
        jarir_tasks = [
            query_worker_jarir(client, q, lang, label)
            for q, lang, label in SEARCH_TARGETS
        ]
        jarir_results = await asyncio.gather(*jarir_tasks)

        # Phase 2: Multi-Store Parallel Comparison via Worker
        print("[Phase 2] Running Multi-Store Parallel Price Comparisons (Jarir + eXtra + Noon)...")
        compare_targets = [
            ("macbook pro", "en", "MacBook Pro"),
            ("iphone 16 pro", "en", "iPhone 16 Pro"),
            ("playstation 5", "en", "PlayStation 5"),
            ("rtx 4070", "en", "RTX 4070 Gaming"),
        ]
        compare_tasks = [
            query_worker_compare(client, q, lang, label)
            for q, lang, label in compare_targets
        ]
        compare_results = await asyncio.gather(*compare_tasks)

    elapsed = time.time() - start_time
    print(f"\n[✓] ALL PARALLEL WORKER OPERATIONS COMPLETED IN {elapsed:.2f} SECONDS!\n")

    # Metrics Breakdown
    all_jarir_products = []
    print(f"{'Category Label':<30} | {'Lang':<4} | {'Edge Cache':<10} | {'Latency':<8} | {'Extracted':<9} | {'Total in DB'}")
    print("-" * 80)
    for r in jarir_results:
        label = r["label"]
        lang = r["lang"]
        cache = r.get("cache", "N/A")
        lat = f"{r['latency_sec']}s"
        cnt = str(r["count"])
        tot = str(r.get("total_in_db", "N/A"))
        all_jarir_products.extend(r["products"])
        print(f"{label:<30} | {lang:<4} | {cache:<10} | {lat:<8} | {cnt:<9} | {tot}")

    print("-" * 80)
    print(f"Total Unique Products Ingested via Worker : {len(all_jarir_products):,}")
    print(f"Extraction Speed Throughput               : {len(all_jarir_products)/elapsed:.1f} items/sec")

    # Multi-store Comparison Summary
    print("\n🔍 MULTI-STORE PARALLEL COMPARISON VIA WORKER:")
    for cr in compare_results:
        sm = cr.get("summary", {})
        print(f" - {cr['label']} (Latency: {cr['latency_sec']}s, Worker internal: {cr.get('worker_latency_ms')}ms):")
        print(f"   Jarir: {sm.get('jarir_count', 0)} items | eXtra: {sm.get('extra_count', 0)} items | Noon: {sm.get('noon_count', 0)} items")

    # Export to JSON
    export_path = "cloudflare_worker_harvest_dump.json"
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump({
            "harvester": "Cloudflare Worker Edge Proxy (worker.ts)",
            "timestamp": time.time(),
            "total_elapsed_seconds": round(elapsed, 2),
            "total_products_collected": len(all_jarir_products),
            "jarir_batches": jarir_results,
            "multi_store_comparisons": compare_results,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n[💾] Complete edge harvest dataset saved to: {export_path}")


if __name__ == "__main__":
    asyncio.run(main())
