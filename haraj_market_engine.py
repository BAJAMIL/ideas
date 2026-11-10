import sqlite3
import re
import json
import time
from typing import List, Dict, Any, Optional
from haraj_deep_client import HarajClient

DB_PATH = "haraj_market.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS listings (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        price INTEGER,
        city TEXT,
        neighborhood TEXT,
        seller_username TEXT,
        seller_id INTEGER,
        url TEXT,
        post_date INTEGER,
        first_seen INTEGER,
        last_seen INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        price INTEGER,
        recorded_at INTEGER,
        FOREIGN KEY(post_id) REFERENCES listings(id)
    )
    """)
    conn.commit()
    conn.close()

class HarajMarketEngine:
    def __init__(self):
        init_db()
        self.client = HarajClient()

    def sync_keyword(self, keyword: str) -> Dict[str, Any]:
        """Fetches from public SSR route and upserts to local SQLite database."""
        raw_items = self.client.search(keyword)
        if not raw_items:
            return {"new": 0, "updated": 0, "fetched": 0}

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        now = int(time.time())
        new_count = 0
        updated_count = 0

        for it in raw_items:
            post_id = it.get('id')
            if not post_id:
                continue

            price_dict = it.get('price')
            price_val = None
            if isinstance(price_dict, dict) and price_dict.get('inputPrice'):
                try:
                    price_val = int(price_dict['inputPrice'])
                except (ValueError, TypeError):
                    pass

            title = it.get('title', '')
            city = it.get('city', '')
            neighborhood = it.get('geoNeighborhood', '')
            seller = it.get('authorUsername', '')
            seller_id = it.get('authorId')
            url = f"https://haraj.com.sa/{it.get('URL', '')}"
            post_date = it.get('postDate')

            cur.execute("SELECT price FROM listings WHERE id = ?", (post_id,))
            row = cur.fetchone()
            if row is None:
                cur.execute("""
                INSERT INTO listings (id, title, price, city, neighborhood, seller_username, seller_id, url, post_date, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (post_id, title, price_val, city, neighborhood, seller, seller_id, url, post_date, now, now))
                if price_val is not None:
                    cur.execute("INSERT INTO price_history (post_id, price, recorded_at) VALUES (?, ?, ?)", (post_id, price_val, now))
                new_count += 1
            else:
                old_price = row[0]
                cur.execute("UPDATE listings SET last_seen = ?, price = ? WHERE id = ?", (now, price_val, post_id))
                if price_val is not None and price_val != old_price:
                    cur.execute("INSERT INTO price_history (post_id, price, recorded_at) VALUES (?, ?, ?)", (post_id, price_val, now))
                    updated_count += 1

        conn.commit()
        conn.close()
        return {"new": new_count, "updated": updated_count, "fetched": len(raw_items)}

    def detect_anomalies(self, min_samples=3, threshold_pct=20.0) -> List[Dict[str, Any]]:
        """Calculates market median and detects listings X% below median."""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, title, price, city, neighborhood, seller_username, url FROM listings WHERE price IS NOT NULL AND price > 100")
        rows = cur.fetchall()
        conn.close()

        if len(rows) < min_samples:
            return []

        prices = [r[2] for r in rows]
        prices.sort()
        mid = len(prices) // 2
        median_price = prices[mid] if len(prices) % 2 != 0 else (prices[mid - 1] + prices[mid]) / 2

        deals = []
        for r in rows:
            post_id, title, price, city, neighborhood, seller, url = r
            if price < median_price * (1.0 - threshold_pct / 100.0):
                discount = round((1.0 - (price / median_price)) * 100, 1)
                deals.append({
                    'id': post_id,
                    'title': title,
                    'price': price,
                    'median': median_price,
                    'discount_pct': discount,
                    'location': f"{city} - {neighborhood}" if neighborhood else city,
                    'seller': seller,
                    'url': url
                })
        deals.sort(key=lambda x: x['discount_pct'], reverse=True)
        return deals

if __name__ == "__main__":
    init_db()
    engine = HarajMarketEngine()
    print("1. Syncing live market listings for 'RTX 3060'...")
    res = engine.sync_keyword("RTX 3060")
    print(f"   Sync result: {res}")

    print("2. Detecting Arbitrage Deals (>20% below median)...")
    deals = engine.detect_anomalies(threshold_pct=20.0)
    print(f"   Found {len(deals)} anomalous undervalued listings:")
    for d in deals:
        print(f"   * [{d['price']} SAR] (Market Median: {d['median']} SAR, Discount: -{d['discount_pct']}%)")
        print(f"     Item: {d['title']}")
        print(f"     Seller: {d['seller']} ({d['location']})")
        print(f"     URL: {d['url']}")
