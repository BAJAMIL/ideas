"""
Jarir Bookstore Complete Category Taxonomy Harvester
Extracts the live multi-tier category tree (including icons, product counts, 
parent-child relationships, category codes, and URLs) from Jarir's Nuxt 3 state.
"""

import httpx
import json
import re
from typing import Any, Dict, List, Optional


def extract_category_tree(lang: str = "en") -> List[Dict[str, Any]]:
    url = f"https://www.jarir.com/sa-{lang}/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": f"{lang};q=0.9,en;q=0.8",
    }
    resp = httpx.get(url, headers=headers, timeout=20.0)
    resp.raise_for_status()
    text = resp.text

    m = re.search(r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', text, re.DOTALL)
    if not m:
        raise ValueError("Could not find __NUXT_DATA__ script in Jarir homepage.")

    raw_data = json.loads(m.group(1))

    def resolve(val, seen=None):
        if seen is None:
            seen = set()
        if isinstance(val, int) and 0 <= val < len(raw_data):
            if val in seen:
                return None
            seen.add(val)
            target = raw_data[val]
            if isinstance(target, (str, float, bool)) or target is None:
                return target
            if isinstance(target, list):
                if len(target) == 2 and target[0] in ("Reactive", "ShallowReactive"):
                    return resolve(target[1], set(seen))
                return [resolve(x, set(seen)) for x in target]
            if isinstance(target, dict):
                return {k: resolve(v, set(seen)) for k, v in target.items()}
            return target
        elif isinstance(val, list):
            if len(val) == 2 and val[0] in ("Reactive", "ShallowReactive"):
                return resolve(val[1], seen)
            return [resolve(x, seen) for x in val]
        elif isinstance(val, dict):
            return {k: resolve(v, seen) for k, v in val.items()}
        return val

    # Find the categories pointer
    resolved_root = resolve(2)
    categories_ref = None
    menu_key = f"header-mobile-cat-menu-sa_{lang}"
    if isinstance(resolved_root, list) and len(resolved_root) > 1 and isinstance(resolved_root[1], dict):
        cat_menu = resolved_root[1].get(menu_key) or resolved_root[1].get("header-mobile-cat-menu-sa_en")
        if cat_menu and isinstance(cat_menu, dict):
            categories_ref = cat_menu.get("categories")

    if not categories_ref:
        # Fallback search in raw_data
        for idx, item in enumerate(raw_data):
            if isinstance(item, dict) and "header-mobile-cat-menu-sa_en" in item:
                cat_menu = resolve(item["header-mobile-cat-menu-sa_en"])
                categories_ref = cat_menu.get("categories")
                break

    if not categories_ref:
        raise ValueError("Failed to locate categories array in Nuxt data.")

    raw_categories = categories_ref if isinstance(categories_ref, list) else resolve(categories_ref)

    def clean_category(cat: Dict[str, Any], level: int = 1) -> Dict[str, Any]:
        if isinstance(cat, list) and len(cat) == 2:
            cat = cat[1]
        
        children = []
        for child in cat.get("children_data", []) or []:
            if isinstance(child, list) and len(child) == 2:
                child = child[1]
            if isinstance(child, dict) and child.get("name"):
                children.append(clean_category(child, level + 1))

        url_path = cat.get("url_path") or f"{cat.get('slug', '')}.html"
        full_url = f"https://www.jarir.com/sa-{lang}/{url_path}" if url_path else ""

        return {
            "name": cat.get("name", ""),
            "slug": cat.get("slug", ""),
            "category_code": str(cat.get("category_code") or cat.get("id") or ""),
            "id": cat.get("id"),
            "product_count": cat.get("product_count", 0),
            "level": level,
            "url": full_url,
            "icon": cat.get("category_icon_image") or "",
            "color": cat.get("category_menu_color") or "",
            "subcategories_count": len(children),
            "subcategories": children,
        }

    tree = []
    for c in raw_categories:
        if isinstance(c, list) and len(c) == 2:
            c = c[1]
        if isinstance(c, dict) and c.get("name"):
            tree.append(clean_category(c, level=1))

    return tree


if __name__ == "__main__":
    print("Extracting full Jarir category taxonomy for English (sa-en)...")
    en_tree = extract_category_tree("en")
    print(f"Extracted {len(en_tree)} top-level categories.")

    with open("jarir_taxonomy_tree.json", "w", encoding="utf-8") as f:
        json.dump(en_tree, f, ensure_ascii=False, indent=2)

    total_subcats = sum(c["subcategories_count"] for c in en_tree)
    total_prods = sum(c["product_count"] for c in en_tree)
    print(f"Total Top Categories: {len(en_tree)}")
    print(f"Total Direct Subcategories: {total_subcats}")
    print(f"Total Products Represented: {total_prods:,}")
    print("Saved rich taxonomy to jarir_taxonomy_tree.json successfully!")
