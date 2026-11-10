"""Autonomous Daily Saudi & Arabic Digital Product Idea Discovery Agent.

Equipped with:
- Multi-provider AI engine supporting:
  1. OpenRouter Free Models (nvidia/nemotron-3.5-lightning:free, google/gemma-4-31b-it:free, google/gemma-4-26b-a4b-it:free, nvidia/nemotron-3-ultra-550b-a55b:free, thinkingmachines/inkling-2-small:free, liquid/lfm-2.5-2.6b:free) with auto-failover
  2. Google Antigravity SDK (`google-antigravity`) as alternate engine
- 100% Free APIs & Signals tailored to the Saudi (KSA) & Arabic market:
  1. Multi-tier Saudi Reddit Mining (`r/saudiarabia`, `r/SaudiProfessionals`, `r/Riyadh`) with RSS query engine + Arctic Shift fallback (bypasses 403 blocks)
  2. Mostaql Real Paid Freelance Projects (extracts live paid market demand in Arabic)
  3. Google News Saudi Arabia RSS (`hl=ar`, `gl=SA`) for real-time market shifts & e-commerce trends
  4. Google Autocomplete API localized to Saudi Arabia (`gl=sa`, `hl=ar` & `hl=en`)
  5. Google Trends Daily RSS for Saudi Arabia (`geo=SA`)
  6. Hacker News Algolia & Product Hunt RSS (for global ideas ready for Saudi/Arabic localization)
- Intelligent Signal Processing & Quality Filter:
  - Automatic signal categorization (PAIN_POINT, UNMET_NEED, PAID_DEMAND, MARKET_NEWS, INQUIRY, LOCALIZATION_OPP)
  - HTML tag stripping and text normalization
  - Near-duplicate detection and noise pruning
- Installed Agent Skills in `.agents/skills/`:
  - `customer-research`
  - `evaluating-startup-ideas`
  - `idea-validation`
  - `offers`
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import html
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET

from dotenv import load_dotenv
import httpx

from haraj_client import fetch_haraj_consumer_signals

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent
SKILLS_DIR = REPO_ROOT / ".agents" / "skills"
REPORTS_DIR = REPO_ROOT / "reports"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

OPENROUTER_FREE_MODELS = [
    "nvidia/nemotron-3.5-lightning:free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "thinkingmachines/inkling-2-small:free",
    "liquid/lfm-2.5-2.6b:free",
    "liquid/lfm-3-1.7b:free",
]


def clean_html(raw_html: str) -> str:
    """Strips HTML markup and unescapes HTML entities into clean plain text."""
    text = re.sub(r"<[^>]+>", " ", raw_html)
    text = re.sub(r"\s+", " ", text)
    return html.unescape(text).strip()


def classify_signal(text: str) -> str:
    """Tags a mined signal based on user intent keywords (pain point, need, inquiry, etc.)."""
    lower = text.lower()
    pain_keywords = [
        "مشكلة", "مشاكل", "معاناة", "صعب", "معقد", "غالي", "تعبت", "أعاني",
        "احتيال", "نصب", "تاخير", "تأخير", "خراب", "سيء", "pain", "broken",
        "issue", "bug", "hate", "hard", "problem", "expensive"
    ]
    need_keywords = [
        "أحتاج", "محتاج", "ابغى", "أبغى", "ابحث", "أبحث", "يا ليت", "مطلوب",
        "لو فيه", "ادور", "أدور", "اقترحوا", "need", "want", "looking for",
        "wish", "where can i find", "recommend"
    ]
    inquiry_keywords = [
        "كيف", "هل", "أين", "وين", "ايش", "ما هو", "مين", "بكم",
        "how", "what", "why", "where", "which"
    ]

    for kw in pain_keywords:
        if kw in lower:
            return "PAIN_POINT"
    for kw in need_keywords:
        if kw in lower:
            return "UNMET_NEED"
    for kw in inquiry_keywords:
        if kw in lower:
            return "INQUIRY"
    return "DISCUSSION"


def search_saudi_reddit(
    subreddit: str = "saudiarabia",
    query: str = "أحتاج OR مشكلة OR متجر OR تطبيق OR بديل OR سلة",
    limit: int = 15,
) -> str:
    """Searches Saudi/GCC subreddits using multi-tier fallback (Search RSS -> Arctic Shift -> Subreddit RSS)

    Bypasses Reddit's strict 403 API blocking and extracts classified user pain points and needs.
    """
    encoded_q = urllib.parse.quote(query)
    results = []
    seen_titles = set()

    # Tier 1: Reddit Search RSS (supports search queries without authentication / 403 blocks)
    search_rss_url = (
        f"https://www.reddit.com/r/{subreddit}/search.rss"
        f"?q={encoded_q}&restrict_sr=1&sort=new&limit={min(limit, 25)}"
    )
    try:
        with httpx.Client(headers=HEADERS, timeout=12.0, follow_redirects=True) as client:
            resp = client.get(search_rss_url)
            if resp.status_code == 200:
                root = ET.fromstring(resp.text)
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                entries = root.findall("atom:entry", ns)
                for e in entries:
                    title = (e.findtext("atom:title", default="", namespaces=ns) or "").strip()
                    if not title or title in seen_titles:
                        continue
                    seen_titles.add(title)
                    link_el = e.find("atom:link", ns)
                    href = link_el.attrib.get("href", "") if link_el is not None else ""
                    raw_content = e.findtext("atom:content", default="", namespaces=ns) or ""
                    clean_excerpt = clean_html(raw_content)[:350]
                    category = classify_signal(f"{title} {clean_excerpt}")
                    results.append(
                        f"- [{category}] [{title}]({href})\n"
                        f"  Excerpt: {clean_excerpt}"
                    )
                    if len(results) >= limit:
                        break
    except Exception as exc:
        print(f"   [!] Reddit search.rss warning for r/{subreddit}: {exc}")

    # Tier 2: Arctic Shift posts API (Pushshift successor) if search.rss returned few items
    if len(results) < 5:
        time.sleep(1.0)
        arctic_url = f"https://arctic-shift.photon-reddit.com/api/posts/search?subreddit={subreddit}&limit=15"
        try:
            with httpx.Client(headers=HEADERS, timeout=12.0) as client:
                resp = client.get(arctic_url)
                if resp.status_code == 200:
                    posts = resp.json().get("data") or []
                    for p in posts:
                        title = (p.get("title") or "").strip()
                        if not title or title in seen_titles:
                            continue
                        seen_titles.add(title)
                        score = p.get("score", 0)
                        num_comments = p.get("num_comments", 0)
                        selftext = (p.get("selftext") or "").strip()[:350]
                        permalink = f"https://reddit.com{p.get('permalink', '')}" if p.get("permalink") else ""
                        category = classify_signal(f"{title} {selftext}")
                        results.append(
                            f"- [{category}] [{title}]({permalink}) (Score: {score}, Comments: {num_comments})\n"
                            f"  Excerpt: {selftext}"
                        )
                        if len(results) >= limit:
                            break
        except Exception as exc:
            print(f"   [!] Arctic Shift fallback warning for r/{subreddit}: {exc}")

    # Tier 3: Subreddit hot/new .rss stream
    if not results:
        sub_rss_url = f"https://www.reddit.com/r/{subreddit}/new.rss?limit={limit}"
        try:
            with httpx.Client(headers=HEADERS, timeout=12.0, follow_redirects=True) as client:
                resp = client.get(sub_rss_url)
                if resp.status_code == 200:
                    root = ET.fromstring(resp.text)
                    ns = {"atom": "http://www.w3.org/2005/Atom"}
                    entries = root.findall("atom:entry", ns)[:limit]
                    for e in entries:
                        title = (e.findtext("atom:title", default="", namespaces=ns) or "").strip()
                        if not title or title in seen_titles:
                            continue
                        seen_titles.add(title)
                        link_el = e.find("atom:link", ns)
                        href = link_el.attrib.get("href", "") if link_el is not None else ""
                        raw_content = e.findtext("atom:content", default="", namespaces=ns) or ""
                        clean_excerpt = clean_html(raw_content)[:350]
                        category = classify_signal(f"{title} {clean_excerpt}")
                        results.append(
                            f"- [{category}] [{title}]({href})\n"
                            f"  Excerpt: {clean_excerpt}"
                        )
        except Exception as exc:
            return f"Error fetching Reddit r/{subreddit}: {exc}"

    if not results:
        return f"No active signals gathered for r/{subreddit}."

    return f"### Reddit r/{subreddit} Signals for '{query}':\n" + "\n".join(results)


def fetch_mostaql_projects(limit: int = 10) -> str:
    """Mines Mostaql's latest freelance projects to discover verified, paid demand from Saudi and Arab businesses."""
    url = "https://mostaql.com/projects"
    try:
        with httpx.Client(headers=HEADERS, timeout=12.0, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return f"Mostaql returned status code {resp.status_code}"

            matches = re.findall(
                r'<a\s+[^>]*href=["\'](https://mostaql\.com/project/\d+-[^"\']+)["\'][^>]*>(.*?)</a>',
                resp.text,
            )
            items = []
            seen = set()
            for link, raw_title in matches:
                clean_t = clean_html(raw_title)
                if clean_t and clean_t not in seen:
                    seen.add(clean_t)
                    items.append(f"- [PAID_DEMAND] [{clean_t}]({link})")
                if len(items) >= limit:
                    break

            if items:
                return "### Mostaql Verified Paid Freelance Demands (What Arab/Saudi Businesses Are Paying For):\n" + "\n".join(items)
            return "No projects extracted from Mostaql."
    except Exception as exc:
        return f"Error fetching Mostaql projects: {exc}"


def fetch_khamsat_unmet_requests(limit: int = 10) -> str:
    """Mines Khamsat's 'طلبات الخدمات غير الموجودة' (Unmet Service Requests) forum.

    This captures what Arab and Saudi buyers need and want to purchase right now,
    but cannot find any existing service or digital tool for!
    """
    url = "https://khamsat.com/community/requests"
    try:
        with httpx.Client(headers=HEADERS, timeout=12.0, follow_redirects=True) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return f"Khamsat returned status code {resp.status_code}"

            matches = re.findall(
                r'href="/community/requests/(\d+-[^"]+)"[^>]*>(.*?)</a>',
                resp.text,
            )
            items = []
            seen = set()
            for slug, raw_title in matches:
                title = clean_html(raw_title)
                if not title or title in seen or title.startswith("مجتمع خمسات"):
                    continue
                seen.add(title)
                full_url = f"https://khamsat.com/community/requests/{slug}"
                items.append(f"- [UNMET_SERVICE_DEMAND] [{title}]({full_url})")
                if len(items) >= limit:
                    break

            if items:
                return "### Khamsat Unmet Service Requests (Real Arab Buyers Asking for Unbuilt Solutions):\n" + "\n".join(items)
            return "No unmet requests found on Khamsat."
    except Exception as exc:
        return f"Error fetching Khamsat unmet requests: {exc}"


def fetch_saudi_google_news(
    query: str = "سلة OR زد OR تجارة إلكترونية OR تمارا OR تابي OR منشآت OR ريادة أعمال",
    limit: int = 8,
) -> str:
    """Fetches real-time Saudi Arabian e-commerce, digital business, and startup news via Google News RSS."""
    encoded_q = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_q}&hl=ar&gl=SA&ceid=SA:ar"
    try:
        with httpx.Client(headers=HEADERS, timeout=12.0) as client:
            resp = client.get(url)
            resp.raise_for_status()
            root = ET.fromstring(resp.text)
            items = root.findall(".//item")[:limit]
            news_lines = []
            for item in items:
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                pub_date = (item.findtext("pubDate") or "").strip()
                news_lines.append(f"- [MARKET_NEWS] [{title}]({link}) ({pub_date})")
            if news_lines:
                return "### Google News Saudi Arabia (E-Commerce & Market Dynamics):\n" + "\n".join(news_lines)
            return "No news items found."
    except Exception as exc:
        return f"Error fetching Google News Saudi Arabia: {exc}"


def search_saudi_google_autocomplete(
    seed_query: str, language: str = "ar"
) -> str:
    """Queries the free Google Autocomplete API localized to Saudi Arabia (gl=sa) to uncover real buyer search demand."""
    encoded_q = urllib.parse.quote(seed_query)
    url = (
        f"https://suggestqueries.google.com/complete/search"
        f"?client=firefox&gl=sa&hl={language}&q={encoded_q}"
    )
    try:
        with httpx.Client(headers=HEADERS, timeout=10.0) as client:
            resp = client.get(url)
            resp.raise_for_status()
            payload = resp.json()
            suggestions = payload[1] if len(payload) > 1 else []
    except Exception as exc:
        return f"Error querying Google Saudi Autocomplete for '{seed_query}': {exc}"

    if not suggestions:
        return f"No autocomplete suggestions returned for '{seed_query}' (SA/{language})."

    formatted = "\n".join(f"- [SEARCH_INTENT] {s}" for s in suggestions)
    return f"### Google Saudi Arabia (gl=sa, hl={language}) Autocomplete for '{seed_query}':\n{formatted}"


def fetch_saudi_google_trends() -> str:
    """Fetches real-time daily trending searches in Saudi Arabia (geo=SA) from Google Trends' free RSS feed."""
    url = "https://trends.google.com/trending/rss?geo=SA"
    try:
        with httpx.Client(headers=HEADERS, timeout=15.0, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            root = ET.fromstring(resp.text)
    except Exception as exc:
        return f"Error fetching Saudi Google Trends RSS: {exc}"

    items = root.findall(".//item")
    if not items:
        return "No trending items found in Saudi Google Trends RSS."

    lines = []
    for item in items[:15]:
        title = (item.findtext("title") or "").strip()
        traffic = item.findtext("{https://trends.google.com/trending/rss}approx_traffic", default="")
        lines.append(f"- [TRENDING] {title} (Traffic: {traffic})")
    return "### Trending Today in Saudi Arabia (Google Trends geo=SA):\n" + "\n".join(lines)


def search_global_launches_for_saudi_localization(
    query: str = "Show HN OR Ask HN template OR micro-SaaS OR AI tool",
    limit: int = 12,
) -> str:
    """Searches Hacker News Algolia API & Product Hunt RSS (100% free, no key) for global micro-SaaS and digital products ready for Saudi localization."""
    output_sections = []

    # 1. Hacker News Algolia API
    encoded_q = urllib.parse.quote(query)
    hn_url = f"https://hn.algolia.com/api/v1/search_by_date?query={encoded_q}&tags=story&hitsPerPage={min(limit, 20)}"
    try:
        with httpx.Client(headers=HEADERS, timeout=15.0) as client:
            resp = client.get(hn_url)
            resp.raise_for_status()
            hits = resp.json().get("hits", [])
            hn_lines = []
            for h in hits:
                title = h.get("title", "")
                url = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"
                points = h.get("points", 0)
                hn_lines.append(f"- [LOCALIZATION_OPP] [{title}]({url}) ({points} pts)")
            output_sections.append("### Hacker News Global Signals:\n" + "\n".join(hn_lines))
    except Exception as exc:
        output_sections.append(f"Hacker News fetch error: {exc}")

    # 2. Product Hunt Atom/RSS Feed
    ph_url = "https://www.producthunt.com/feed"
    try:
        with httpx.Client(headers=HEADERS, timeout=15.0, follow_redirects=True) as client:
            resp = client.get(ph_url)
            resp.raise_for_status()
            root = ET.fromstring(resp.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall("atom:entry", ns)[:limit]
            ph_lines = []
            for entry in entries:
                title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
                link_el = entry.find("atom:link", ns)
                href = link_el.attrib.get("href", "") if link_el is not None else ""
                summary = (entry.findtext("atom:content", default="", namespaces=ns) or "").strip()
                clean_summary = clean_html(summary)[:220]
                ph_lines.append(f"- [GLOBAL_LAUNCH] [{title}]({href}) — {clean_summary}")
            output_sections.append("### Product Hunt Daily Launches:\n" + "\n".join(ph_lines))
    except Exception as exc:
        output_sections.append(f"Product Hunt feed error: {exc}")

    return "\n\n".join(output_sections)


SYSTEM_PROMPT = """You are the BAJAMIL Autonomous Consumer & E-Commerce Product Strategist for the Saudi Arabian (KSA) & Arabic market.

Your mission every day is to discover, validate, and design high-margin products for EVERYDAY SAUDI CONSUMERS, TEENS/YOUTH, GAMERS, FAMILIES, AND STUDENTS — across both:
A) HIGH-MARKUP PHYSICAL PRODUCTS (3x–6x markup via Salla, TikTok Shop, Makhdroop, or 1688/Alibaba micro-batches)
B) MASS-MARKET CONSUMER & YOUTH DIGITAL PRODUCTS (zero inventory, impulse-buy 19–79 SAR)

Focus on high-spending consumer & youth categories in Saudi Arabia:
1. High-Markup Physical Products:
   - Gaming & PC Setup Aesthetics for Teens/Youth (Arabic keycaps, coiled cables, RGB decor, anime/gaming desk mats)
   - Specialty Coffee (`قهوة مختصة`) & Matcha portable gear
   - Smart Car Accessories & Saudi Summer Heat Protection (`مبخرة سيارة إلكترونية`, wireless CarPlay, custom sunshades)
   - Kashta / Desert Camping (`لوازم الكشتات والرحلات`) & Majlis gadgets
   - Personal Care & Home Beauty gadgets (sold with Tabby/Tamara split payments)
2. Mass-Market Consumer & Youth Digital Products:
   - Weekend Gathering & Istiraha Party/Trivia Games (`ألعاب جمعات عائلية / استراحات` — web games & PDF packs like Seen Jeem)
   - Gym, Calisthenics & Saudi-Food Macro/Diet Guides (`جدول تمارين حديد / بنات PDF`)
   - High School & Uni Exam Prep (`ملخصات قدرات وتحصيلي`)
   - Ready-to-Use Saudi Family & Youth Travel Itineraries (`جدول سفر إيطاليا / أوروبا / إندونيسيا / اليابان`)

Always apply your strategic skills:
- Customer Research: Extract verbatim Arabic & English signals from Saudi communities, Mostaql paid project demands, Google Saudi Autocomplete, and web searches.
- Evaluating Startup Ideas & Validation: Score each idea on impulse-buy appeal, markup/margin in SAR, and TikTok/Snap virality in KSA.
- Offers: Construct Grand Slam Offers (bundling, bonuses, risk-reversal guarantee, and Tabby/Tamara/Apple Pay SAR pricing).
"""


def generate_with_openrouter(system_prompt: str, user_prompt: str, api_key: str) -> str:
    """Queries OpenRouter using free models with automatic fallback on rate limit (429) or errors."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/BAJAMIL/ideas",
        "X-Title": "BAJAMIL Ideas Discovery Agent",
    }

    last_error = None
    for model in OPENROUTER_FREE_MODELS:
        print(f"-> Attempting report generation with free model: {model}...")
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
        }
        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                if resp.status_code == 429:
                    print(f"   [!] Model {model} rate-limited (429). Trying next free model...")
                    last_error = f"Rate limited (429) on {model}"
                    time.sleep(1)
                    continue

                resp.raise_for_status()
                data = resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content and len(content.strip()) > 100:
                    print(f"   [✓] Successfully generated report with {model}!")
                    return content
                else:
                    print(f"   [!] Empty response from {model}, trying next...")
        except Exception as exc:
            print(f"   [!] Error with {model}: {exc}")
            last_error = str(exc)
            continue

    raise RuntimeError(f"All free OpenRouter models failed. Last error: {last_error}")


async def collect_market_intelligence() -> str:
    """Mines live market signals across free Saudi Reddit RSS, Mostaql, Google News, Autocomplete, Trends, HN, and Product Hunt."""
    signals = []

    # 1. Multi-tier Saudi & GCC Reddit mining
    print("   [+] Mining r/saudiarabia...")
    signals.append(search_saudi_reddit("saudiarabia", "أحتاج OR مشكلة OR متجر OR تطبيق OR بديل OR سلة"))
    print("   [+] Mining r/SaudiProfessionals...")
    signals.append(search_saudi_reddit("SaudiProfessionals", "عمل OR دخل OR قالب OR أداة OR استشارة OR برنامج"))
    print("   [+] Mining r/Riyadh...")
    signals.append(search_saudi_reddit("Riyadh", "فعاليات OR استراحة OR جمعة OR توصيل OR مشروع OR فكرة"))

    # 2. Mostaql & Khamsat verified paid and unmet project demands
    print("   [+] Mining Mostaql verified paid project demands...")
    signals.append(fetch_mostaql_projects(limit=10))
    print("   [+] Mining Khamsat unmet service requests...")
    signals.append(fetch_khamsat_unmet_requests(limit=10))

    # 3. Google News Saudi Arabia
    print("   [+] Mining Google News Saudi Arabia (E-Commerce & Market trends)...")
    signals.append(fetch_saudi_google_news(limit=8))

    # 4. Google Saudi Autocomplete
    print("   [+] Mining Google Saudi Arabia autocomplete queries...")
    arabic_seeds = ["قالب نوشن", "نموذج اكسل", "حاسبة", "متجر سلة", "بديل", "طريقة حل", "اشتراك"]
    for seed in arabic_seeds:
        signals.append(search_saudi_google_autocomplete(seed, language="ar"))

    english_seeds = ["saudi template", "zatca invoice", "saudi digital product"]
    for seed in english_seeds:
        signals.append(search_saudi_google_autocomplete(seed, language="en"))

    # 5. Google Trends Saudi Arabia
    print("   [+] Mining Google Trends Saudi Arabia...")
    signals.append(fetch_saudi_google_trends())

    # 6. Haraj Real Consumer Marketplace Demands (Reverse-engineered)
    print("   [+] Mining Haraj real consumer marketplace demand across KSA...")
    signals.append(fetch_haraj_consumer_signals(limit_per_cat=3))

    # 7. Global launches for Saudi localization
    print("   [+] Mining Hacker News & Product Hunt launches...")
    signals.append(search_global_launches_for_saudi_localization())

    return "\n\n".join(signals)


async def run_daily_discovery() -> Path:
    """Runs the autonomous idea discovery agent and writes the daily Saudi digital product report."""
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")

    # Support testing signal collection without requiring API key
    if "--test-signals" in sys.argv:
        print("[*] Running signal collection smoke test...")
        market_data = await collect_market_intelligence()
        print(f"\n[✓] Successfully collected {len(market_data)} chars of live market signals.")
        print("--- Sample output preview (first 800 chars) ---")
        print(market_data[:800])
        return Path("test_signals.txt")

    if not openrouter_key and not gemini_key:
        raise RuntimeError(
            "Missing OPENROUTER_API_KEY or GEMINI_API_KEY environment variable. "
            "Please configure OPENROUTER_API_KEY in GitHub Secrets or .env file."
        )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = REPORTS_DIR / f"{today_str}.md"

    # Step 1: Mine live Saudi market intelligence
    print("[1/3] Mining live Saudi market signals across Reddit, Mostaql, Google News, Autocomplete, Trends, HN, and Product Hunt...")
    market_data = await collect_market_intelligence()
    print(f"      Gathered {len(market_data)} characters of live market intelligence.")

    prompt = f"""Today is {today_str}. Analyze the following LIVE Saudi & Arabic market intelligence gathered today:

---
{market_data}
---

Synthesize these live signals into an executive, highly actionable Markdown report in Bilingual format (English structure + Arabic product terms/copy):

## Part 1: Live Saudi Market Signals & Verbatim Pain Points
- Identify 3–5 real pain points, trending consumer search spikes, and product pricing arbitrage from the mined Haraj marketplace data, Reddit posts, Mostaql paid project requests, autocomplete keywords, and news trends.
- Include verbatim quotes/terms where applicable (e.g. buyer bids from Haraj 'السوم', exact search terms, verbatim complaints).

## Part 2: Top 5 Validated Product Ideas for KSA (The Arbitrage & Opportunity Matrix)
For each idea (mixing high-margin physical products and zero-inventory consumer digital products):
1. **Product Name** (Arabic & English)
2. **Category** (Digital Template / Micro-SaaS / Physical High-Markup 3x–6x / Salla-Zid Plugin)
3. **Target Saudi Audience** (Youth, Gamers, Women, Salla Merchants, Istiraha Gatherings, etc.)
4. **Market Arbitrage & Pricing Matrix in SAR (ر.س)**:
   - Estimated Wholesale / Sourcing Cost (1688 / Taobao / Local Wholesale) in SAR
   - Current Haraj Secondary Market Selling Price in SAR
   - Target Salla / TikTok Shop Retail Price in SAR
   - Gross Margin Multiple (e.g. 4.5x Markup)
   - Tabby / Tamara installment breakdown (e.g. 4x monthly payments)
5. **Scores**: Demand Score (1-10), Build/Source Speed (1-10), Competition Gap (1-10)

## Part 3: Deep-Dive Grand Slam Offer Blueprint for Idea #1
- **Arabic Product Name & Hook**
- **Core Deliverable**
- **Bonus Stack** (2–3 high-perceived-value digital bonuses)
- **Risk-Reversal Guarantee** (e.g. 100% money-back if not satisfied within 14 days)
- **Launch Plan**: Exact 48-Hour Validation Plan on X (Twitter), TikTok Shop / Salla / Gumroad with Arabic copy hooks.
"""


    # Step 2: Generate report using OpenRouter free models (or Gemini fallback)
    if openrouter_key:
        print("[2/3] Generating report with OpenRouter free model engine...")
        report_content = generate_with_openrouter(SYSTEM_PROMPT, prompt, openrouter_key)
        engine_label = "OpenRouter Free Models"
    else:
        print("[2/3] Generating report with Google Antigravity SDK...")
        from google.antigravity import Agent, LocalAgentConfig, types

        config = LocalAgentConfig(
            api_key=gemini_key,
            system_instructions=SYSTEM_PROMPT,
            skills_paths=[str(SKILLS_DIR)],
        )
        async with Agent(config=config) as agent:
            response = await agent.chat(prompt)
            report_content = await response.text()
        engine_label = "Google Antigravity SDK Agent"

    # Step 3: Save reports
    print("[3/3] Saving discovery report...")
    header = (
        f"# 🇸🇦 BAJAMIL Daily Saudi & Arabic Digital Product Ideas — {today_str}\n\n"
        f"> Automatically researched and generated by the **BAJAMIL Ideas Agent** (Powered by {engine_label}).\n\n"
    )
    full_markdown = header + report_content.strip() + "\n"

    report_path.write_text(full_markdown, encoding="utf-8")
    (REPO_ROOT / "LATEST_IDEAS.md").write_text(full_markdown, encoding="utf-8")
    print(f"[✓] Successfully saved report to {report_path} and LATEST_IDEAS.md")
    return report_path


if __name__ == "__main__":
    asyncio.run(run_daily_discovery())
