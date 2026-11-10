#!/usr/bin/env python3
"""
Jarir Bookstore CLI Explorer (BAJAMIL Ideas)
Interactive command-line tool to query, filter, and inspect Jarir Bookstore's catalog.

Usage:
  # Tech & Electronics
  python jarir_cli.py search "laptop" --limit 5
  python jarir_cli.py filter "laptop" --brand "Apple" --ram "16 GB RAM" --min-price 4000 --max-price 8000

  # Books & Literature (Over 710,000 titles)
  python jarir_cli.py books "رواية" --author "فيكتور هوجو" --format "غلاف ورقي" --lang ar
  python jarir_cli.py books "Harry Potter" --author "Rowling" --format "Paperback" --lang en
  python jarir_cli.py books "تطوير الذات" --jarir-only --lang ar
  python jarir_cli.py isbn "9781408855713"

  # School & Office Stationery
  python jarir_cli.py stationery "دفتر" --size "A4" --brand "Roco"
  python jarir_cli.py stationery "ألوان" --brand "Faber-Castell"

  # Common
  python jarir_cli.py autocomplete "ipad"
  python jarir_cli.py lookup 692656
  python jarir_cli.py export "روايات" --output novels.json --lang ar
"""

import argparse
import json
import sys
from jarir_client import JarirClient


def main():
    parser = argparse.ArgumentParser(
        description="Jarir Bookstore Private API Explorer (Tech, Books & Stationery) — BAJAMIL Ideas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Command: search
    search_p = subparsers.add_parser("search", help="Search Jarir products across all categories")
    search_p.add_argument("query", help="Search keyword (e.g. laptop, رواية, دفتر, بلايستيشن)")
    search_p.add_argument("--lang", default="en", choices=["en", "ar"], help="Language index")
    search_p.add_argument("--limit", type=int, default=10, help="Number of items to show")
    search_p.add_argument("--sort", choices=["price", "relevance"], default=None, help="Sort attribute")
    search_p.add_argument("--order", choices=["ascending", "descending"], default="descending", help="Sort order")

    # Command: books (Dedicated for Jarir's 710,000+ Book Catalog)
    books_p = subparsers.add_parser("books", help="Search Jarir's 710,000+ Arabic & English books catalog")
    books_p.add_argument("query", help="Book title, keyword, or subject (e.g. رواية, تاريخ, برمجة, Harry Potter)")
    books_p.add_argument("--author", help="Author name (e.g. 'J. K. Rowling', 'طه حسين', 'فيكتور هوجو')")
    books_p.add_argument("--format", help="Binding format (e.g. 'غلاف ورقي', 'Paperback', 'Hardcover', 'كتاب الكتروني')")
    books_p.add_argument("--jarir-only", action="store_true", help="Restrict to official Jarir Publications (اصدارات جرير)")
    books_p.add_argument("--min-price", type=float, help="Minimum price in SAR")
    books_p.add_argument("--max-price", type=float, help="Maximum price in SAR")
    books_p.add_argument("--lang", default="ar", choices=["ar", "en"], help="Language index ('ar' Arabic / 'en' English)")
    books_p.add_argument("--limit", type=int, default=10, help="Number of books to show")

    # Command: stationery (Dedicated for School, Office & Art Supplies)
    stat_p = subparsers.add_parser("stationery", help="Search school, office, and art supplies")
    stat_p.add_argument("query", help="Item name (e.g. دفتر, قلم, ألوان, شنطة, notebook, pen, marker)")
    stat_p.add_argument("--size", help="Paper dimensions (e.g. 'A4', 'A5', 'Letter', 'A3')")
    stat_p.add_argument("--brand", help="Stationery brand (e.g. 'Roco', 'Faber-Castell', 'Parker', 'Stabilo')")
    stat_p.add_argument("--type", help="Product type (e.g. 'مفكرة', 'قلم ماركر', 'Drawing Pad')")
    stat_p.add_argument("--min-price", type=float, help="Minimum price in SAR")
    stat_p.add_argument("--max-price", type=float, help="Maximum price in SAR")
    stat_p.add_argument("--lang", default="ar", choices=["ar", "en"], help="Language index")
    stat_p.add_argument("--limit", type=int, default=10, help="Number of items to show")

    # Command: isbn (Lookup Book by ISBN Barcode)
    isbn_p = subparsers.add_parser("isbn", help="Lookup a book by ISBN-10 or ISBN-13 barcode")
    isbn_p.add_argument("isbn", help="ISBN number (e.g. 9781408855713)")
    isbn_p.add_argument("--lang", default="en", choices=["en", "ar"], help="Language index")

    # Command: filter (Hardware & Electronics)
    filter_p = subparsers.add_parser("filter", help="Search with advanced hardware facets (Tech & Electronics)")
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
    auto_p = subparsers.add_parser("autocomplete", help="Get live search suggestions & consumer intent")
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

    # Command: categories (Full category taxonomy tree, product counts & icons)
    cats_p = subparsers.add_parser("categories", help="Explore complete Jarir category taxonomy tree, icons & product counts")
    cats_p.add_argument("--tree", action="store_true", help="Print full hierarchical category tree with all subcategories")
    cats_p.add_argument("--parent", help="Filter by parent category slug or code (e.g. 'electronics-mobiles', 'books')")
    cats_p.add_argument("--lang", default="en", choices=["en", "ar"], help="Language index")
    cats_p.add_argument("--json", action="store_true", help="Output raw JSON taxonomy")

    # Command: category (Lookup single category details)
    cat_p = subparsers.add_parser("category", help="Lookup details, icons, and subcategories for a category")
    cat_p.add_argument("identifier", help="Category slug, code, or name (e.g. 'smartphones', '21001', 'bags-travel-accessories')")
    cat_p.add_argument("--lang", default="en", choices=["en", "ar"], help="Language index")

    # Command: browse (Browse products in a category)
    browse_p = subparsers.add_parser("browse", help="Browse products in a category")
    browse_p.add_argument("category", help="Category slug, code, or name (e.g. 'laptops', 'smartphones')")
    browse_p.add_argument("--limit", type=int, default=10, help="Number of products to show")
    browse_p.add_argument("--lang", default="en", choices=["en", "ar"], help="Language index")

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
        print(f"[✓] Found {res['total']} products total. Showing top {len(res['products'])}:\n")
        for i, p in enumerate(res["products"], 1):
            disc_str = f" [Saved {p.discount_amount} SAR]" if p.discount_amount else ""
            author_str = f" | Author: {p.author}" if p.author else ""
            format_str = f" | Format: {p.book_format}" if p.book_format else ""
            print(f"{i:2d}. {p.title}")
            print(f"    Price: {p.price:,.2f} SAR{disc_str} | SKU: {p.sku} | Brand/Pub: {p.publisher or p.brand or 'N/A'}{author_str}{format_str}")
            if p.url:
                print(f"    URL:   {p.url}")
            print()

    elif args.command == "books":
        print(f"[*] Searching Jarir Books for '{args.query}' (author={args.author}, format={args.format}, lang={args.lang})...")
        res = client.search_books(
            query=args.query,
            author=args.author,
            book_format=args.format,
            lang=args.lang,
            jarir_publications_only=args.jarir_only,
            min_price=args.min_price,
            max_price=args.max_price,
            num_results=args.limit,
        )
        print(f"[✓] Found {res['total']} matching books. Showing top {len(res['products'])}:\n")
        for i, b in enumerate(res["products"], 1):
            auth_line = f"    Author:    {b.author or 'N/A'}"
            format_line = f" | Format: {b.book_format or 'N/A'}"
            isbn_line = f" | ISBN: {b.isbn}" if b.isbn else ""
            pub_line = f" | Publisher: {b.publisher or 'N/A'}"
            print(f"{i:2d}. 📖 {b.title}")
            print(f"{auth_line}{format_line}{isbn_line}{pub_line}")
            print(f"    Price:     {b.price:,.2f} SAR | SKU: {b.sku}")
            if b.url:
                print(f"    URL:       {b.url}")
            print()

    elif args.command == "stationery":
        print(f"[*] Searching Stationery & Supplies for '{args.query}' (size={args.size}, brand={args.brand}, lang={args.lang})...")
        res = client.search_stationery(
            query=args.query,
            paper_size=args.size,
            brand=args.brand,
            product_type=args.type,
            lang=args.lang,
            min_price=args.min_price,
            max_price=args.max_price,
            num_results=args.limit,
        )
        print(f"[✓] Found {res['total']} matching stationery items. Showing top {len(res['products'])}:\n")
        for i, s in enumerate(res["products"], 1):
            size_line = f" | Size: {s.paper_size}" if s.paper_size else ""
            type_line = f" | Type: {s.product_type or s.category_desc}" if (s.product_type or s.category_desc) else ""
            print(f"{i:2d}. ✏️ {s.title}")
            print(f"    Brand: {s.brand or 'N/A'}{size_line}{type_line} | Price: {s.price:,.2f} SAR | SKU: {s.sku}")
            if s.url:
                print(f"    URL:   {s.url}")
            print()

    elif args.command == "isbn":
        print(f"[*] Resolving Book by ISBN: {args.isbn}...")
        b = client.get_book_by_isbn(args.isbn, lang=args.lang)
        if not b:
            print("[❌] No book found matching that ISBN.")
            sys.exit(1)
        print(f"[✓] Book Found:")
        print(f"  Title:       {b.title}")
        print(f"  Author:      {b.author or 'N/A'}")
        print(f"  Format:      {b.book_format or 'N/A'}")
        print(f"  ISBN:        {b.isbn or args.isbn}")
        print(f"  Publisher:   {b.publisher or b.brand or 'N/A'}")
        print(f"  Price:       {b.price:,.2f} SAR")
        print(f"  SKU:         {b.sku}")
        print(f"  Image (CDN): {b.direct_cdn_image}")
        print(f"  URL:         {b.url}")

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
        print(f"[✓] Matching items: {res['total']}. Showing top {len(res['products'])}:\n")
        for i, p in enumerate(res["products"], 1):
            print(f"{i:2d}. {p.title}")
            print(f"    Price: {p.price:,.2f} SAR | SKU: {p.sku} | Brand: {p.brand or 'N/A'}")
            if p.url:
                print(f"    URL:   {p.url}")
            print()

    elif args.command == "autocomplete":
        print(f"[*] Fetching live autocomplete for '{args.query}'...")
        sug = client.get_search_suggestions(args.query, lang=args.lang)
        print(f"[✓] Suggestions ({len(sug.suggested_products)} returned):")
        for i, s in enumerate(sug.suggested_products, 1):
            print(f"  {i}. {s}")

    elif args.command == "lookup":
        print(f"[*] Looking up SKU: {args.sku}...")
        p = client.get_product_by_sku(args.sku, lang=args.lang)
        if not p:
            print("[❌] Product not found.")
            sys.exit(1)
        print(f"[✓] Product Found:")
        print(f"  Title:       {p.title}")
        print(f"  Price:       {p.price:,.2f} SAR")
        print(f"  SKU:         {p.sku}")
        print(f"  Brand:       {p.brand}")
        if p.author:
            print(f"  Author:      {p.author}")
        if p.book_format:
            print(f"  Format:      {p.book_format}")
        if p.isbn:
            print(f"  ISBN:        {p.isbn}")
        if p.paper_size:
            print(f"  Paper Size:  {p.paper_size}")
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
                "author": p.author,
                "book_format": p.book_format,
                "isbn": p.isbn,
                "paper_size": p.paper_size,
                "model": p.model,
                "url": p.url,
                "image_cdn": p.direct_cdn_image,
                "categories": p.categories,
            }
            for p in res["products"]
        ]
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump({"total": res["total"], "query": args.query, "items": data}, f, ensure_ascii=False, indent=2)
        print(f"[✓] Successfully saved {len(data)} items to {args.output}!")

    elif args.command == "categories":
        tree = client.get_category_tree(lang=args.lang)

        if args.parent:
            parent_cat = client.get_category(args.parent, lang=args.lang)
            if not parent_cat:
                print(f"[!] Parent category '{args.parent}' not found.")
                sys.exit(1)
            tree = parent_cat.get("subcategories", [])
            print(f"[*] Showing subcategories for '{parent_cat.get('name')}' ({len(tree)} found):")
        else:
            print(f"[*] Jarir Bookstore Category Taxonomy (Shop By Category Menu):")
            print(f"    Total Departments: {len(tree)} | Live catalog mapped with Akeneo CDN Icons & product counts.\n")

        if args.json:
            print(json.dumps(tree, ensure_ascii=False, indent=2))
            return

        for i, c in enumerate(tree, 1):
            name = c.get("name")
            code = c.get("category_code")
            slug = c.get("slug")
            count = c.get("product_count", 0)
            icon = c.get("icon")
            sub_count = c.get("subcategories_count", len(c.get("subcategories", [])))

            print(f"{i:2d}. {name} [Code: {code} | Slug: {slug}]")
            print(f"    Products: {count:,} items | Subcategories: {sub_count}")
            print(f"    URL:      {c.get('url')}")
            if icon:
                print(f"    Icon:     {icon}")

            if args.tree and c.get("subcategories"):
                for sub in c.get("subcategories", []):
                    sub_name = sub.get("name")
                    sub_code = sub.get("category_code")
                    sub_count_val = sub.get("product_count", 0)
                    print(f"      ├── {sub_name} (Code: {sub_code}, Products: {sub_count_val:,})")
                    if sub.get("subcategories"):
                        for sub3 in sub.get("subcategories", [])[:3]:
                            print(f"      │    └── {sub3.get('name')} (Code: {sub3.get('category_code')})")
            print()

    elif args.command == "category":
        cat = client.get_category(args.identifier, lang=args.lang)
        if not cat:
            print(f"[!] Category '{args.identifier}' not found in taxonomy tree.")
            sys.exit(1)

        print(f"[*] Category Details: {cat.get('name')}")
        print(f"  Code:          {cat.get('category_code')}")
        print(f"  ID:            {cat.get('id')}")
        print(f"  Slug:          {cat.get('slug')}")
        print(f"  Level:         {cat.get('level')}")
        print(f"  Product Count: {cat.get('product_count', 0):,} items")
        print(f"  Menu Color:    #{cat.get('color')}" if cat.get('color') else "  Menu Color:    N/A")
        print(f"  URL:           {cat.get('url')}")
        print(f"  Icon CDN:      {cat.get('icon')}")
        subs = cat.get("subcategories", [])
        print(f"  Subcategories: {len(subs)}")
        for s in subs:
            print(f"    - {s.get('name')} (Code: {s.get('category_code')}, Products: {s.get('product_count', 0):,})")

    elif args.command == "browse":
        print(f"[*] Browsing products for category '{args.category}' (limit={args.limit}, lang={args.lang})...")
        res = client.browse_category(args.category, num_results=args.limit, lang=args.lang)
        print(f"[✓] Found {res['total']} products total. Showing top {len(res['products'])}:\n")
        for i, p in enumerate(res["products"], 1):
            disc_str = f" [Saved {p.discount_amount} SAR]" if p.discount_amount else ""
            author_str = f" | Author: {p.author}" if p.author else ""
            format_str = f" | Format: {p.book_format}" if p.book_format else ""
            print(f"{i:2d}. {p.title}")
            print(f"    Price: {p.price:,.2f} SAR{disc_str} | SKU: {p.sku} | Brand: {p.brand or 'N/A'}{author_str}{format_str}")
            if p.url:
                print(f"    URL:   {p.url}")
            print()


if __name__ == "__main__":
    main()
