#!/usr/bin/env python3
"""
Jarir Bookstore CLI Explorer (BAJAMIL Ideas)
Interactive command-line tool to query, filter, and inspect Jarir Bookstore's catalog.

Usage:
  python jarir_cli.py search "rtx" --limit 5
  python jarir_cli.py filter "laptop" --brand "Apple" --ram "16 GB RAM" --min-price 4000 --max-price 8000
  python jarir_cli.py autocomplete "ipad"
  python jarir_cli.py lookup 692656
  python jarir_cli.py export "gaming monitor" --output monitors.json
"""

import argparse
import json
import sys
from jarir_client import JarirClient


def main():
    parser = argparse.ArgumentParser(
        description="Jarir Bookstore Private API Explorer (BAJAMIL Ideas)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Command: search
    search_p = subparsers.add_parser("search", help="Search Jarir products")
    search_p.add_argument("query", help="Search keyword (e.g. laptop, iphone, بلايستيشن)")
    search_p.add_argument("--lang", default="en", choices=["en", "ar"], help="Language index")
    search_p.add_argument("--limit", type=int, default=10, help="Number of items to show")
    search_p.add_argument("--sort", choices=["price", "relevance"], default=None, help="Sort attribute")
    search_p.add_argument("--order", choices=["ascending", "descending"], default="descending", help="Sort order")

    # Command: filter
    filter_p = subparsers.add_parser("filter", help="Search with advanced hardware facets")
    filter_p.add_argument("query", help="Base keyword (e.g. laptop, desktop)")
    filter_p.add_argument("--brand", help="Brand name (e.g. Apple, HP, Asus)")
    filter_p.add_argument("--min-price", type=float, help="Minimum price in SAR")
    filter_p.add_argument("--max-price", type=float, help="Maximum price in SAR")
    filter_p.add_argument("--ram", help="RAM capacity (e.g. '16 GB RAM', '32 GB RAM')")
    filter_p.add_argument("--storage", help="Storage (e.g. '512 GB', '1000 GB', '2 TB')")
    filter_p.add_argument("--os", help="OS (e.g. 'macOS', 'Windows 11 Home')")
    filter_p.add_argument("--screen", help="Screen size (e.g. '14\"', '15.6\"')")
    filter_p.add_argument("--color", help="Color (e.g. 'Silver', 'Black')")
    filter_p.add_argument("--lang", default="en", choices=["en", "ar"])
    filter_p.add_argument("--limit", type=int, default=10)

    # Command: autocomplete
    auto_p = subparsers.add_parser("autocomplete", help="Get live search suggestions")
    auto_p.add_argument("query", help="Prefix or keyword to autocomplete")
    auto_p.add_argument("--lang", default="en", choices=["en", "ar"])

    # Command: lookup
    lookup_p = subparsers.add_parser("lookup", help="Lookup exact product details by SKU")
    lookup_p.add_argument("sku", help="Jarir SKU number (e.g. 692656)")
    lookup_p.add_argument("--lang", default="en", choices=["en", "ar"])

    # Command: export
    export_p = subparsers.add_parser("export", help="Export search results to JSON")
    export_p.add_argument("query", help="Keyword to search and export")
    export_p.add_argument("--output", "-o", default="jarir_export.json", help="Output JSON path")
    export_p.add_argument("--lang", default="en", choices=["en", "ar"])
    export_p.add_argument("--limit", type=int, default=50)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    client = JarirClient()

    if args.command == "search":
        print(f"[*] Searching Jarir for '{args.query}' (lang={args.lang}, limit={args.limit})...")
        res = client.search_products(
            args.query,
            lang=args.lang,
            num_results=args.limit,
            sort_by=args.sort,
            sort_order=args.order,
        )
        print(f"[\u2713] Found {res['total']} products total. Showing top {len(res['products'])}:\n")
        for i, p in enumerate(res["products"], 1):
            disc_str = f" [Saved {p.discount_amount} SAR]" if p.discount_amount else ""
            print(f"{i:2d}. {p.title}")
            print(f"    Price: {p.price:,.2f} SAR{disc_str} | SKU: {p.sku} | Brand: {p.brand or 'N/A'}")
            if p.url:
                print(f"    URL:   {p.url}")
            print()

    elif args.command == "filter":
        print(f"[*] Applying hardware filters on '{args.query}'...")
        res = client.search_products(
            args.query,
            lang=args.lang,
            num_results=args.limit,
            brand=args.brand,
            min_price=args.min_price,
            max_price=args.max_price,
            ram=args.ram,
            storage=args.storage,
            os=args.os,
            screen_size=args.screen,
            color=args.color,
        )
        print(f"[\u2713] Matching items: {res['total']}. Showing top {len(res['products'])}:\n")
        for i, p in enumerate(res["products"], 1):
            print(f"{i:2d}. {p.title}")
            print(f"    Price: {p.price:,.2f} SAR | SKU: {p.sku} | Brand: {p.brand or 'N/A'}")
            if p.url:
                print(f"    URL:   {p.url}")
            print()

    elif args.command == "autocomplete":
        print(f"[*] Fetching live autocomplete for '{args.query}'...")
        sug = client.get_search_suggestions(args.query, lang=args.lang)
        print(f"[\u2713] Suggestions ({len(sug.suggested_products)} returned):")
        for i, s in enumerate(sug.suggested_products, 1):
            print(f"  {i}. {s}")

    elif args.command == "lookup":
        print(f"[*] Looking up SKU: {args.sku}...")
        p = client.get_product_by_sku(args.sku, lang=args.lang)
        if not p:
            print("[\u274c] Product not found.")
            sys.exit(1)
        print(f"[\u2713] Product Found:")
        print(f"  Title:       {p.title}")
        print(f"  Price:       {p.price:,.2f} SAR")
        print(f"  SKU:         {p.sku}")
        print(f"  Brand:       {p.brand}")
        print(f"  Model:       {p.model}")
        print(f"  Image (CDN): {p.direct_cdn_image}")
        print(f"  URL:         {p.url}")
        if p.categories:
            print(f"  Categories:  {' > '.join(p.categories)}")

    elif args.command == "export":
        print(f"[*] Exporting up to {args.limit} results for '{args.query}' to {args.output}...")
        res = client.search_products(args.query, lang=args.lang, num_results=args.limit)
        data = [
            {
                "sku": p.sku,
                "title": p.title,
                "price_sar": p.price,
                "brand": p.brand,
                "model": p.model,
                "url": p.url,
                "image_cdn": p.direct_cdn_image,
                "categories": p.categories,
            }
            for p in res["products"]
        ]
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump({"total": res["total"], "query": args.query, "items": data}, f, ensure_ascii=False, indent=2)
        print(f"[\u2713] Successfully saved {len(data)} items to {args.output}!")


if __name__ == "__main__":
    main()
