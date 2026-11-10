"""Autonomous Daily Saudi & Arabic Digital Product Idea Discovery Agent.

Equipped with:
- Multi-provider AI engine supporting:
  1. OpenRouter Free Models (nvidia/nemotron-3.5-lightning:free, google/gemma-4-31b-it:free, google/gemma-4-26b-a4b-it:free, thinkingmachines/inkling-2-small:free) with auto-failover
  2. Google Antigravity SDK (`google-antigravity`) as alternate engine
- 100% Free APIs tailored to the Saudi (KSA) & Arabic market:
  1. Reddit Saudi/GCC JSON API (`r/saudiarabia`, `r/SaudiProfessionals`, `r/Riyadh`, etc.)
  2. Google Autocomplete API localized to Saudi Arabia (`gl=sa`, `hl=ar` & `hl=en`)
  3. Google Trends Daily RSS for Saudi Arabia (`geo=SA`)
  4. Hacker News Algolia & Product Hunt RSS (for global ideas ready for Saudi/Arabic localization)
- Installed Agent Skills in `.agents/skills/`:
  - `customer-research`
  - `evaluating-startup-ideas`
  - `idea-validation`
  - `offers`
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
import urllib.parse
import xml.etree.ElementTree as ET

from dotenv import load_dotenv
import httpx

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent
SKILLS_DIR = REPO_ROOT / ".agents" / "skills"
REPORTS_DIR = REPO_ROOT / "reports"

HEADERS = {
    "User-Agent": "BAJAMIL-SaudiIdeaAgent/1.0 (+https://github.com/BAJAMIL/ideas)"
}

OPENROUTER_FREE_MODELS = [
    "nvidia/nemotron-3.5-lightning:free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "thinkingmachines/inkling-2-small:free",
    "liquid/lfm-2.5-2.6b:free",
]


def search_saudi_reddit(
    subreddit: str = "saudiarabia",
    query: str = "أحتاج OR مشكلة OR مشروع OR Salla OR tool OR app",
    limit: int = 15,
) -> str:
    """Searches Saudi and Arabic subreddits using Reddit's free JSON API for pain points and product ideas."""
    encoded_q = urllib.parse.quote(query)
    url = (
        f"https://www.reddit.com/r/{subreddit}/search.json"
        f"?q={encoded_q}&restrict_sr=1&sort=new&t=month&limit={min(limit, 25)}"
    )
    try:
        with httpx.Client(headers=HEADERS, timeout=15.0, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        return f"Error fetching r/{subreddit} for query '{query}': {exc}"

    posts = data.get("data", {}).get("children", [])
    if not posts:
        return f"No recent posts found in r/{subreddit} for '{query}'."

    results = []
    for item in posts:
        p = item.get("data", {})
        title = p.get("title", "").strip()
        selftext = (p.get("selftext", "") or "").strip()[:400]
        score = p.get("score", 0)
        num_comments = p.get("num_comments", 0)
        permalink = f"https://www.reddit.com{p.get('permalink', '')}"
        results.append(
            f"- [{title}]({permalink}) (Score: {score}, Comments: {num_comments})\n"
            f"  Excerpt: {selftext}"
        )
    return f"### Reddit r/{subreddit} Results for '{query}':\n" + "\n".join(results)


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

    formatted = "\n".join(f"- {s}" for s in suggestions)
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
        title = item.findtext("title", default="").strip()
        traffic = item.findtext("{https://trends.google.com/trending/rss}approx_traffic", default="")
        lines.append(f"- {title} (Traffic: {traffic})")
    return "### Trending Today in Saudi Arabia (Google Trends geo=SA):\n" + "\n".join(lines)


def search_global_launches_for_saudi_localization(
    query: str = "Show HN OR Ask HN template OR micro-SaaS OR AI tool",
    limit: int = 12,
) -> str:
    """Searches Hacker News Algolia API & Product Hunt RSS (100% free, no key) for global micro-SaaS and digital products that can be localized for Saudi Arabia / Arabic."""
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
                hn_lines.append(f"- [{title}]({url}) ({points} pts)")
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
                title = entry.findtext("atom:title", default="", namespaces=ns).strip()
                link_el = entry.find("atom:link", ns)
                href = link_el.attrib.get("href", "") if link_el is not None else ""
                summary = (entry.findtext("atom:content", default="", namespaces=ns) or "").strip()
                clean_summary = summary.replace("<p>", "").replace("</p>", " ")[:220]
                ph_lines.append(f"- [{title}]({href}) — {clean_summary}")
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
- Customer Research: Extract verbatim Arabic & English signals from Saudi communities, Google Saudi Autocomplete, and web searches.
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


async def run_daily_discovery() -> Path:
    """Runs the autonomous idea discovery agent and writes the daily Saudi digital product report."""
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")

    if not openrouter_key and not gemini_key:
        raise RuntimeError(
            "Missing OPENROUTER_API_KEY or GEMINI_API_KEY environment variable. "
            "Please configure OPENROUTER_API_KEY in GitHub Secrets or .env file."
        )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = REPORTS_DIR / f"{today_str}.md"

    # Step 1: Mine live Saudi market intelligence
    print("[1/3] Mining live Saudi market signals across Reddit, Google Trends, Autocomplete, HN, and Product Hunt...")
    signals = []
    signals.append(search_saudi_reddit("saudiarabia", "أحتاج OR مشكلة OR مشروع OR Salla OR متجر OR فكرة"))
    signals.append(search_saudi_reddit("SaudiProfessionals", "عمل OR دخل OR قالب OR أداة OR استشارة"))
    signals.append(search_saudi_reddit("Riyadh", "فعاليات OR استراحة OR جمعة OR توصيل OR مشروع"))

    for seed in ["قالب نوشن", "نموذج اكسل", "حاسبة", "متجر سلة"]:
        signals.append(search_saudi_google_autocomplete(seed, language="ar"))

    for seed in ["saudi template", "zatca invoice", "saudi digital product"]:
        signals.append(search_saudi_google_autocomplete(seed, language="en"))

    signals.append(fetch_saudi_google_trends())
    signals.append(search_global_launches_for_saudi_localization())

    market_data = "\n\n".join(signals)
    print(f"      Gathered {len(market_data)} characters of live market intelligence.")

    prompt = f"""Today is {today_str}. Analyze the following LIVE Saudi & Arabic market intelligence gathered today:

---
{market_data}
---

Synthesize these live signals into a complete, professional, and actionable Markdown report in Bilingual format (English structure + Arabic product terms/copy):

## Part 1: Live Saudi Market Signals & Verbatim Pain Points
- Identify 3–5 real pain points and high-interest topics from the mined Reddit posts, autocomplete keywords, and trends. Include verbatim quotes/terms where applicable.

## Part 2: Top 5 Validated Product Ideas for KSA
For each idea (mixing high-margin physical products and zero-inventory consumer digital products):
1. **Product Name** (Arabic & English)
2. **Category** (Digital Template / Micro-SaaS / Physical High-Markup 3x–6x)
3. **Target Saudi Audience** (Youth, Gamers, Women, Salla Merchants, Istiraha Gatherings, etc.)
4. **Demand Score (1-10)**, **Build/Source Speed (1-10)**, **Competition Gap (1-10)**
5. **Pricing Strategy in SAR (ر.س)** (Impulse-buy sweet spots, Tabby/Tamara installment options)

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
        engine_label = "OpenRouter Free Models (NVIDIA Nemotron / Google Gemma)"
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
