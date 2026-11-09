"""Autonomous Daily Saudi & Arabic Digital Product Idea Discovery Agent.

Built with the Google Antigravity SDK (`google-antigravity`) and equipped with:
- Built-in Web Search (`SEARCH_WEB`) and URL Scraping (`READ_URL_CONTENT`)
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
import urllib.parse
import xml.etree.ElementTree as ET

from dotenv import load_dotenv
from google.antigravity import Agent, LocalAgentConfig, types
import httpx

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent
SKILLS_DIR = REPO_ROOT / ".agents" / "skills"
REPORTS_DIR = REPO_ROOT / "reports"

HEADERS = {
    "User-Agent": "BAJAMIL-SaudiIdeaAgent/1.0 (+https://github.com/BAJAMIL/ideas)"
}


def search_saudi_reddit(
    subreddit: str = "saudiarabia",
    query: str = "أحتاج OR مشكلة OR مشروع OR Salla OR tool OR app",
    limit: int = 15,
) -> str:
    """Searches Saudi and Arabic subreddits using Reddit's free JSON API for pain points and product ideas.

    Recommended subreddits: 'saudiarabia', 'SaudiProfessionals', 'Riyadh', 'Jeddah', 'arabs', 'SaaS', 'Entrepreneur'.

    Args:
        subreddit: The subreddit name without 'r/' (e.g., 'saudiarabia', 'SaudiProfessionals').
        query: Search keywords in Arabic or English (e.g., 'سلة OR زد', 'مشكلة', 'spreadsheet', 'freelance').
        limit: Number of recent matching posts to return (max 25).
    """
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
    """Queries the free Google Autocomplete API localized to Saudi Arabia (gl=sa) to uncover real buyer search demand.

    Args:
        seed_query: Partial search phrase in Arabic or English (e.g., 'قالب نوشن', 'نموذج إكسل', 'حاسبة', 'تطبيق لـ', 'saudi template').
        language: Language code, 'ar' for Arabic or 'en' for English.
    """
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
    """Searches Hacker News Algolia API & Product Hunt RSS (100% free, no key) for global micro-SaaS and digital products that can be localized for Saudi Arabia / Arabic.

    Args:
        query: Search query for Hacker News Algolia API.
        limit: Max items to fetch from each source.
    """
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

Always apply your installed skills from `.agents/skills`:
- `customer-research`: Extract verbatim Arabic & English signals from Saudi communities, Google Saudi Autocomplete, and web searches.
- `evaluating-startup-ideas` & `idea-validation`: Score each idea on impulse-buy appeal, markup/margin in SAR, and TikTok/Snap virality in KSA.
- `offers`: Construct Grand Slam Offers (bundling, bonuses, risk-reversal guarantee, and Tabby/Tamara/Apple Pay SAR pricing).
"""


async def run_daily_discovery() -> Path:
    """Runs the autonomous Antigravity agent and writes the daily Saudi digital product report."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing GEMINI_API_KEY environment variable. "
            "Get a free key at https://aistudio.google.com/app/api-keys and add it to GitHub Secrets."
        )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = REPORTS_DIR / f"{today_str}.md"

    config = LocalAgentConfig(
        api_key=api_key,
        system_instructions=SYSTEM_PROMPT,
        skills_paths=[str(SKILLS_DIR)],
        tools=[
            search_saudi_reddit,
            search_saudi_google_autocomplete,
            fetch_saudi_google_trends,
            search_global_launches_for_saudi_localization,
        ],
        capabilities=types.CapabilitiesConfig(
            agent_behavior=types.AgentBehavior.AUTONOMOUS,
            enabled_tools=[
                types.BuiltinTools.SEARCH_WEB,
                types.BuiltinTools.READ_URL_CONTENT,
                types.BuiltinTools.VIEW_FILE,
            ],
        ),
        budget_config=types.BudgetConfig(
            max_model_calls=15,
            max_tool_calls=25,
        ),
    )

    prompt = f"""Today is {today_str}. Run a comprehensive daily discovery session for the Saudi Arabian (KSA) & Arabic digital products market:

1. Call `search_saudi_reddit` across `saudiarabia`, `SaudiProfessionals`, and `Riyadh` to mine recent complaints, workarounds, business needs, and questions.
2. Call `search_saudi_google_autocomplete` in Arabic (`ar`) for seeds like `'قالب نوشن'`, `'نموذج اكسل'`, `'حاسبة'`, `'متجر سلة'` and in English (`en`) for `'saudi template'`, `'zatca'`.
3. Call `fetch_saudi_google_trends` and `search_global_launches_for_saudi_localization` to see trending topics in KSA and global micro-SaaS/templates that lack an Arabic/Saudi version.
4. Use `search_web` if needed to check Salla App Store, Zid, Mostaql, or Haraj trends.
5. Synthesize your findings into a complete, actionable Markdown report in Bilingual format (English + Arabic terms/copy) containing:
   - **Part 1: Live Saudi Market Signals & Verbatim Pain Points** (with links & quotes)
   - **Part 2: Top 5 Validated Digital Product Ideas for KSA** (scored on Demand, Build Speed, Competition Gap, and Monetization in SAR)
   - **Part 3: Deep-Dive Grand Slam Offer Blueprint for Idea #1** (using the `offers` skill: Arabic & English Product Name, Core Deliverable, Bonus Stack, Risk-Reversal Guarantee, Price in SAR, and 48-Hour Validation Plan on X/TikTok/Salla/Gumroad).
"""

    async with Agent(config=config) as agent:
        response = await agent.chat(prompt)
        report_content = await response.text()

    header = (
        f"# 🇸🇦 BAJAMIL Daily Saudi & Arabic Digital Product Ideas — {today_str}\n\n"
        f"> Automatically researched and generated by the **BAJAMIL Google Antigravity SDK Agent**.\n\n"
    )
    full_markdown = header + report_content.strip() + "\n"

    report_path.write_text(full_markdown, encoding="utf-8")
    (REPO_ROOT / "LATEST_IDEAS.md").write_text(full_markdown, encoding="utf-8")
    print(f"Saved report to {report_path}")
    return report_path


if __name__ == "__main__":
    asyncio.run(run_daily_discovery())
