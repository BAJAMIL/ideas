"""
Jarir Bookstore Private API Client (Typed Python 3.11+)
Reverse-engineered from Jarir Bookstore KSA (https://www.jarir.com/sa-en/).
Powered by Jarir's live AI Discovery & Search Engine (Constructor.io).

Comprehensive Coverage:
- Over 710,000+ Books across Arabic & English indexes (Arabic Books, English Books, Jarir Publications).
- Rich Book Facets & Metadata: Author (auth), Book Format (bofo: Paperback, Hardcover, eBook, Audiobook, Board Book), ISBN, Publisher, Genre, Reading Age.
- Office, School & Art Stationery: Notebooks (A4, A5, Letter), Pens, Art Markers, Planners, School Bags (Roco, Faber-Castell, Parker).
- Consumer Tech & Hardware: Laptops, PCs, Gaming Consoles, Phones, Displays, Tablets.
- Dual Arabic (ar-SA) and English (en-SA) search indexes.
- Real-time product pricing (SAR), discounts, SKUs, and stock information.
- Direct SKU lookup and high-res media URL generation on Akeneo CDN.
- Autocomplete and real-time search term suggestions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.parse
import httpx


@dataclass
class JarirProduct:
    sku: str
    title: str
    price: float
    currency: str = "SAR"
    brand: Optional[str] = None
    model: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    discount_amount: Optional[float] = None
    # Books & Literature fields
    author: Optional[str] = None
    book_format: Optional[str] = None  # e.g. Paperback, Hardcover, Ebook, Audiobook, غلاف ورقي, غلاف مقوى, كتاب الكتروني
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    genre: Optional[str] = None
    reading_age: Optional[str] = None
    # Stationery, School & Office Supplies fields
    product_type: Optional[str] = None  # e.g. Notebook, Pens, Art Markers, Bookmark, اشارة مرجعية
    category_desc: Optional[str] = None  # e.g. 'كتب عربية', 'English Books', 'اصدارات جرير', 'مفكرة', 'الشنط'
    paper_size: Optional[str] = None  # e.g. A4, A5, Letter, A3
    item_number: Optional[str] = None
    raw_metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_book(self) -> bool:
        """Determines if the product is an Arabic or English book / publication."""
        desc = (self.category_desc or "").lower()
        bofo = (self.book_format or "").lower()
        return bool(
            self.isbn
            or self.author
            or bofo in [
                "paperback", "hardcover", "ebook", "audiobook", "board book",
                "غلاف ورقي", "غلاف مقوى", "كتاب الكتروني", "كتاب صوتي", "كتاب مقوى", "غلاف مقوى فني"
            ]
            or any(kw in desc for kw in ["book", "كتاب", "كتب", "اصدارات جرير", "رواية"])
        )

    @property
    def is_stationery(self) -> bool:
        """Determines if the product is office, school, or art stationery."""
        desc = (self.category_desc or "").lower()
        ptype = (self.product_type or "").lower()
        return bool(
            self.paper_size
            or any(kw in desc for kw in [
                "مفكرة", "دفتر", "قلم", "ألوان", "شنط", "stationery", "notebook",
                "pen", "pencil", "marker", "art", "أدوات مكتبية", "مدرسية"
            ])
            or any(kw in ptype for kw in ["notebook", "pen", "marker", "pencil", "pad", "sketch", "bookmark", "مفكرة", "قلم"])
        )

    @property
    def direct_cdn_image(self) -> str:
        """Returns direct high-resolution Akeneo CDN image URL."""
        return f"https://ak-asset.jarir.com/akeneo-prod/asset/saas/{self.sku}.jpg"


@dataclass
class JarirCategory:
    name: str
    slug: str
    category_code: str
    id: Optional[int] = None
    product_count: int = 0
    level: int = 1
    url: str = ""
    icon: str = ""
    color: str = ""
    subcategories: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def subcategories_count(self) -> int:
        return len(self.subcategories)


@dataclass
class JarirSearchSuggestion:
    query: str
    suggested_products: List[str] = field(default_factory=list)


class JarirClient:
    """Production client for Jarir Bookstore's catalog & search APIs."""

    # Extracted production index keys from Jarir Nuxt frontend
    INDEX_KEYS = {
        "en": "key_KcSYfmQTEwRpBnd9",
        "ar": "key_g0Gi7pKaE5cyqDGl",
    }
    CONSTRUCTOR_API_BASE = "https://ac.cnstrc.com"
    JARIR_BASE_URL = "https://www.jarir.com"

    def __init__(self, timeout: float = 12.0):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
            "Accept-Language": "ar,en;q=0.9",
        }
        self.client = httpx.Client(headers=self.headers, timeout=timeout)

    def _get_key(self, lang: str) -> str:
        return self.INDEX_KEYS.get(lang.lower()[:2], self.INDEX_KEYS["en"])

    def search_products(
        self,
        query: str,
        lang: str = "en",
        page: int = 1,
        num_results: int = 24,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        # Books & Publications Facets
        book_format: Optional[str] = None,
        category_desc: Optional[str] = None,
        reading_age: Optional[str] = None,
        genre: Optional[str] = None,
        # Stationery & Paper Facets
        paper_size: Optional[str] = None,
        product_type: Optional[str] = None,
        # Hardware & Tech Facets
        ram: Optional[str] = None,
        storage: Optional[str] = None,
        os: Optional[str] = None,
        screen_size: Optional[str] = None,
        color: Optional[str] = None,
        year: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "descending",
    ) -> Dict[str, Any]:
        """
        Searches Jarir products with multi-attribute facet filtering.
        
        Args:
            query: Keyword to search (e.g. 'laptop', 'رواية', 'دفتر', 'قلم', 'ألوان').
            lang: 'en' for English index, 'ar' for Arabic index.
            page: Page number (1-indexed).
            num_results: Number of results to return per page.
            brand: Filter by brand / publisher (e.g. 'Apple', 'Roco', 'Bloomsbury', 'Penguin').
            min_price: Minimum price in SAR.
            max_price: Maximum price in SAR.
            book_format: Book binding / format (e.g. 'Paperback', 'Hardcover', 'غلاف ورقي', 'غلاف مقوى', 'كتاب الكتروني').
            category_desc: Product code description (e.g. 'كتب عربية', 'English Books', 'اصدارات جرير', 'مفكرة').
            reading_age: Age range filter (e.g. '7-12 سنة', 'أكثر من 20 سنة').
            genre: Literary genre (e.g. 'أكشن ومغامرة').
            paper_size: Stationery paper dimensions (e.g. 'A4', 'A5', 'Letter').
            product_type: Specific stationery / book type (e.g. 'اشارة مرجعية', 'مفكرة').
            ram: Filter by RAM capacity (e.g. '16 GB RAM', '32 GB RAM').
            storage: Filter by storage capacity (e.g. '512 GB', '1000 GB', '2 TB').
            os: Filter by OS (e.g. 'macOS', 'Windows 11 Home', 'Windows 11 Pro').
            screen_size: Filter by display size (e.g. '14\"', '15.6\"', '16\"').
            color: Filter by color (e.g. 'Silver', 'Black', 'Grey').
            year: Filter by release generation/year (e.g. '2025', '2026').
            sort_by: Sort attribute ('price', 'relevance').
            sort_order: 'ascending' or 'descending'.
        """
        key = self._get_key(lang)
        encoded_query = urllib.parse.quote(query)
        url = f"{self.CONSTRUCTOR_API_BASE}/search/{encoded_query}"

        params: Dict[str, Any] = {
            "key": key,
            "page": page,
            "num_results_per_page": num_results,
        }

        # Apply range filter for price: filters[price]=min-max
        if min_price is not None or max_price is not None:
            min_val = int(min_price) if min_price is not None else 0
            max_val = int(max_price) if max_price is not None else 999999
            params["filters[price]"] = f"{min_val}-{max_val}"

        # Book & Publication facets
        if book_format:
            params["filters[bofo]"] = book_format
        if category_desc:
            params["filters[productcode_description]"] = category_desc
        if reading_age:
            params["filters[reag]"] = reading_age
        if genre:
            params["filters[genr]"] = genre

        # Stationery facets
        if paper_size:
            params["filters[pasi]"] = paper_size
        if product_type:
            params["filters[ptyp]"] = product_type

        # Brand / Publisher
        if brand:
            params["filters[brand]"] = brand

        # Hardware facets
        if ram:
            params["filters[symm]"] = ram
        if storage:
            params["filters[tsca]"] = storage
        if os:
            params["filters[opsy]"] = os
        if screen_size:
            params["filters[scsz]"] = screen_size
        if color:
            params["filters[cofa]"] = color
        if year:
            params["filters[gere]"] = year

        if sort_by:
            params["sort_by"] = sort_by
            params["sort_order"] = sort_order

        resp = self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json().get("response", {})

        total_results = data.get("total_num_results", 0)
        items: List[JarirProduct] = []

        for r in data.get("results", []):
            item_data = r.get("data", {})
            metadata = item_data.get("metadata", {}) or {}

            raw_price = item_data.get("price") or metadata.get("price") or 0.0
            try:
                price_val = float(raw_price)
            except (ValueError, TypeError):
                price_val = 0.0

            # Extract discount from GTM if available
            gtm_raw = metadata.get("additionalDataToReturn")
            categories = []
            discount_amount = None
            if gtm_raw and isinstance(gtm_raw, str):
                try:
                    parsed_gtm = json.loads(gtm_raw)
                    categories = parsed_gtm.get("GTM_categories", [])
                    save_val = parsed_gtm.get("GTM_product_save")
                    if save_val:
                        discount_amount = float(save_val)
                except Exception:
                    pass

            p_url = item_data.get("url")
            full_url = f"{self.JARIR_BASE_URL}/sa-{lang}/{p_url}" if p_url else None
            sku_val = str(item_data.get("sku") or item_data.get("id") or "")

            items.append(
                JarirProduct(
                    sku=sku_val,
                    title=r.get("value", ""),
                    price=price_val,
                    brand=metadata.get("brand") or item_data.get("brand"),
                    model=metadata.get("model"),
                    description=item_data.get("description"),
                    url=full_url,
                    image_url=item_data.get("image_url") or f"https://ak-asset.jarir.com/akeneo-prod/asset/saas/{sku_val}.jpg",
                    categories=categories,
                    discount_amount=discount_amount,
                    author=metadata.get("auth") or None,
                    book_format=metadata.get("bofo") or None,
                    isbn=metadata.get("isbn") or None,
                    publisher=metadata.get("brand") or item_data.get("brand") or None,
                    genre=metadata.get("genr") or None,
                    reading_age=metadata.get("reag") or None,
                    product_type=metadata.get("ptyp") or None,
                    category_desc=metadata.get("productcode_description") or None,
                    paper_size=metadata.get("pasi") or None,
                    item_number=str(metadata.get("item_number") or metadata.get("bar_code1") or "") or None,
                    raw_metadata=metadata,
                )
            )

        return {
            "total": total_results,
            "page": page,
            "products": items,
            "facets": data.get("facets", []),
        }

    def search_books(
        self,
        query: str,
        author: Optional[str] = None,
        book_format: Optional[str] = None,
        lang: str = "ar",
        jarir_publications_only: bool = False,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        num_results: int = 24,
    ) -> Dict[str, Any]:
        """
        Specialized book discovery method querying Jarir's 710,000+ title catalog.
        
        Args:
            query: Title keyword, topic, or author name.
            author: Specific author name filter (if searching in query or checking results).
            book_format: 'غلاف ورقي' (Paperback), 'غلاف مقوى' (Hardcover), 'كتاب الكتروني' (eBook), 'كتاب صوتي' (Audiobook).
            lang: 'ar' for Arabic books / 'en' for English books.
            jarir_publications_only: If True, restricts results to official Jarir Publications (اصدارات جرير).
            min_price: Minimum price in SAR.
            max_price: Maximum price in SAR.
            num_results: Number of results.
        """
        category_desc = None
        if jarir_publications_only:
            category_desc = "اصدارات جرير" if lang == "ar" else "Jarir Publication"
        elif lang == "ar":
            # Can match 'كتب عربية', 'كتاب عربي', or 'اصدارات جرير'
            pass
        elif lang == "en":
            category_desc = "English Books"

        search_q = f"{query} {author}" if author else query
        return self.search_products(
            query=search_q,
            lang=lang,
            book_format=book_format,
            category_desc=category_desc,
            min_price=min_price,
            max_price=max_price,
            num_results=num_results,
        )

    def search_stationery(
        self,
        query: str,
        paper_size: Optional[str] = None,
        brand: Optional[str] = None,
        product_type: Optional[str] = None,
        lang: str = "ar",
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        num_results: int = 24,
    ) -> Dict[str, Any]:
        """
        Specialized stationery, office supplies, school supplies, and art gear discovery.
        
        Args:
            query: e.g. 'دفتر' (Notebook), 'قلم' (Pen), 'ألوان' (Colors), 'شنطة' (Backpack).
            paper_size: 'A4', 'A5', 'Letter', 'A3'.
            brand: 'Roco', 'Faber-Castell', 'Parker', 'Stabilo', 'Pilot'.
            product_type: e.g. 'مفكرة', 'اشارة مرجعية', 'Drawing Pad'.
            lang: 'ar' or 'en'.
            num_results: Number of items.
        """
        return self.search_products(
            query=query,
            lang=lang,
            paper_size=paper_size,
            brand=brand,
            product_type=product_type,
            min_price=min_price,
            max_price=max_price,
            num_results=num_results,
        )

    def get_book_by_isbn(self, isbn: str, lang: str = "en") -> Optional[JarirProduct]:
        """Looks up a book by its ISBN-10 or ISBN-13 barcode."""
        clean_isbn = isbn.replace("-", "").strip()
        res = self.search_products(clean_isbn, lang=lang, num_results=5)
        for p in res.get("products", []):
            if p.isbn and p.isbn.replace("-", "").strip() == clean_isbn:
                return p
        # Fallback to first result if it contains the title
        return res["products"][0] if res.get("products") else None

    def get_product_by_sku(self, sku: str, lang: str = "en") -> Optional[JarirProduct]:
        """Looks up an exact product by its SKU."""
        res = self.search_products(sku, lang=lang, num_results=1)
        for p in res.get("products", []):
            if p.sku == str(sku):
                return p
        return res["products"][0] if res.get("products") else None

    def get_search_suggestions(self, query: str, lang: str = "en") -> JarirSearchSuggestion:
        """Fetch instant search autocomplete and product recommendations."""
        key = self._get_key(lang)
        encoded = urllib.parse.quote(query)
        url = f"{self.CONSTRUCTOR_API_BASE}/autocomplete/{encoded}"

        resp = self.client.get(url, params={"key": key, "num_results_per_section": 6})
        resp.raise_for_status()
        data = resp.json()

        sections = data.get("sections", {})
        queries = [i.get("value") for i in sections.get("Search Suggestions", []) if i.get("value")]
        products = [i.get("value") for i in sections.get("Products", []) if i.get("value")]

        return JarirSearchSuggestion(
            query=query,
            suggested_products=products if products else queries,
        )

    def get_category_tree(self, lang: str = "en", force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Retrieves the complete live multi-level category taxonomy tree.
        Includes icons, codes, URLs, product counts, and subcategories.
        """
        cache_file = (
            Path(__file__).parent / f"jarir_taxonomy_{lang}.json"
            if lang != "en"
            else Path(__file__).parent / "jarir_taxonomy_tree.json"
        )
        if not force_refresh and cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        try:
            from build_jarir_taxonomy import extract_category_tree
            tree = extract_category_tree(lang)
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(tree, f, ensure_ascii=False, indent=2)
            return tree
        except Exception:
            if cache_file.exists():
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return []

    def get_category(self, identifier: str, lang: str = "en") -> Optional[Dict[str, Any]]:
        """
        Finds a category or subcategory by slug, category code, id, or exact name.
        """
        ident_clean = str(identifier).strip().lower().replace(".html", "")
        tree = self.get_category_tree(lang=lang)

        def search_node(node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            slug = str(node.get("slug", "")).lower()
            code = str(node.get("category_code", "")).lower()
            name = str(node.get("name", "")).lower()
            cid = str(node.get("id", "")).lower()
            if ident_clean in (slug, code, name, cid):
                return node
            for child in node.get("subcategories", []):
                found = search_node(child)
                if found:
                    return found
            return None

        for cat in tree:
            found = search_node(cat)
            if found:
                return found
        return None

    def browse_category(
        self,
        identifier: str,
        page: int = 1,
        num_results: int = 24,
        lang: str = "en",
        sort_by: Optional[str] = None,
        sort_order: str = "descending",
    ) -> Dict[str, Any]:
        """
        Browse products inside a specific category slug or category code.
        """
        cat = self.get_category(identifier, lang=lang)
        query = cat.get("name") if cat else identifier
        return self.search_products(
            query=query,
            lang=lang,
            page=page,
            num_results=num_results,
            sort_by=sort_by,
            sort_order=sort_order,
        )


def fetch_jarir_consumer_signals(max_items: int = 10) -> List[Dict[str, Any]]:
    """Standard discovery hook for BAJAMIL Ideas agent across Tech, Books, and Stationery."""
    signals = []
    client = JarirClient()

    targets = [
        ("رواية", "ar", "Arabic Best-Selling Novels & Literature"),
        ("تطوير الذات", "ar", "Self-Development & Jarir Publications"),
        ("دفتر", "ar", "School & Office Stationery (Notebooks)"),
        ("laptop", "en", "Laptops & Computing"),
        ("gaming pc", "en", "Gaming Tech & Hardware"),
    ]

    for q, lang, cat in targets:
        try:
            res = client.search_products(q, lang=lang, num_results=max_items)
            for p in res.get("products", [])[:2]:
                extra_desc = f" by {p.author}" if p.author else ""
                format_desc = f" ({p.book_format})" if p.book_format else ""
                signals.append({
                    "title": f"Jarir {cat}: {p.title}{extra_desc}{format_desc}",
                    "price_sar": p.price,
                    "url": p.url,
                    "sku": p.sku,
                    "brand": p.publisher or p.brand,
                    "author": p.author,
                    "format": p.book_format,
                    "isbn": p.isbn,
                    "source": "Jarir Bookstore (jarir.com)",
                    "type": "CONSUMER_BENCHMARK",
                })
        except Exception:
            continue

    return signals
