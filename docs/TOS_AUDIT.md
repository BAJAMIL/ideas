# Third-Party Source ToS / `robots.txt` Audit

**Date:** 2026-11-11
**Scope:** all data sources wired into `agent.py`, the 12 `*_client.py` marketplace clients, and the Cloudflare Worker's public discovery keys.
**Method:** one isolated research subagent audited each source against primary terms / `robots.txt` files; four highest-stakes claims were independently re-fetched and confirmed by the coordinating agent (Reddit, Google Trends, Golden Scent, Nice One).
**Legal posture assessed:** **commercial/business use** — `SYSTEM_PROMPT` designs priced products (3x–6x markup, 19–79 SAR, Grand Slam Offers, Tabby/Tamara) and the output is published to GitHub Pages + a GitHub Issue. A side project with no revenue is still assessed as business use.

> ⚠️ **This is research, not legal advice.** `VERIFIED` means a primary source was found and read; `UNCLEAR` means no explicit prohibition *or* permission was found — it does **not** mean "compliant". Confirm with counsel before commercial deployment.

---

## 1. Already handled (not re-audited)

| Source | Status |
|---|---|
| **Google News RSS** | Verified against [Google News Terms of Use §2](https://www.google.com/intl/en_us/terms_google_news.html): *"personal use (i.e., non-commercial use)"*, *"may not use the Service to sell a product or service"*. Now **disabled by default** behind `GOOGLE_NEWS_RSS_ENABLED` in `config.py`; when off, no request is made and the source is not listed in the health block. |

## 2. Findings table

| Source | Endpoint used | Governing terms | Commercial use? | `robots.txt` disallow? | Risk | VERIFIED? | Reasoning |
|---|---|---|---|---|---|---|---|
| Google Autocomplete | `suggestqueries.google.com/complete/search?client=firefox&gl=sa&hl=ar&q=…` | [Google ToS](https://policies.google.com/terms) | **UNCLEAR (lean NO)** | Host returns 404 (no robots); `www.google.com/robots.txt` disallows `/search` | **H** | ToS+robots VERIFIED; autocomplete-specific INFERRED | Undocumented internal endpoint hit by automated backend; no commercial licence; Google ToS bars automated access "in violation of robots.txt" and reverse engineering. |
| Google Trends RSS | `trends.google.com/trending/rss?geo=SA` | [Google ToS](https://policies.google.com/terms) | **UNCLEAR** | `trends.google.com/robots.txt` disallows only `/explore?` and `/trends/explore?`; **RSS path not disallowed** (re-fetched, confirmed) | **M** | robots VERIFIED; licence INFERRED | Public feed, not robots-blocked, but no explicit commercial grant — structurally the same gap that got Google News disabled. |
| Reddit RSS (`.rss`, `search.rss`) | `www.reddit.com/r/{sub}/search.rss`, `/new.rss` | [Reddit robots.txt](https://www.reddit.com/robots.txt) → [Public Content Policy](https://support.reddithelp.com/hc/en-us/articles/26410290525844-Public-Content-Policy); [Data API Terms](https://www.redditinc.com/policies/data-api-terms) | **PERSONAL-ONLY / NO** | **`User-agent: * Disallow: /`** (all paths) — re-fetched, confirmed | **H** | VERIFIED | robots.txt points to "research and non-commercial use"; Data API Terms §3.1 requires a separate agreement for commercial purposes, §3.2 bars deriving revenue without written approval. README currently describes "bypassing Reddit's 403 walls". |
| Arctic Shift (Reddit fallback) | `arctic-shift.photon-reddit.com/api/posts/search` | No published ToS found; upstream Reddit content still governed by the above | **UNCLEAR** | n/a (API host) | **H** | site VERIFIED; licence INFERRED | Third-party archive cannot grant rights Reddit itself restricts; exists specifically to bypass Reddit's access controls. |
| Mostaql | `mostaql.com/projects` (HTML regex) | [Terms (Arabic)](https://mostaql.com/p/terms) | **UNCLEAR (lean NO)** | `Disallow: /search*`, `/ajax/`; `/projects` **not** disallowed | **M** | VERIFIED | No explicit automated-collection or commercial-reuse permission; HTML scraping with spoofed browser UA. |
| Khamsat | `khamsat.com/community/requests` (HTML regex) | [Terms (Arabic)](https://khamsat.com/terms) | **UNCLEAR (lean NO)** | `Disallow: /search*`, `/community/search*`, `/ajax/*`; requests board **not** disallowed | **M** | VERIFIED | Terms prohibit harming the site and restrict published content; no API/commercial licence. |
| Hacker News Algolia | `hn.algolia.com/api/v1/search_by_date` | [HN Algolia API](https://hn.algolia.com/api) | **UNCLEAR (lean YES)** | `/robots.txt` 404 (none) | **L** | API docs VERIFIED; licence INFERRED | Public, no-key, documented API explicitly intended for programmatic use; no commercial prohibition found, but no standalone API terms either. |
| Product Hunt feed | `www.producthunt.com/feed` | [Legal](https://www.producthunt.com/legal) (403 on fetch) | **UNCLEAR (lean NO)** | `/feed` **not** disallowed; `/search*` is | **M** | robots VERIFIED; ToS INFERRED | Official OAuth2 API promoted for commercial/volume use; ToS reportedly restricts automated collection — full text not retrievable. |
| Haraj | `graphql.haraj.com.sa`, `matjar.haraj.com.sa/graphql` | No public API terms found | **UNCLEAR** | `haraj.com.sa/robots.txt`: `Allow: /`; gateway is a separate host | **M** | VERIFIED (robots) | Private GraphQL gateway with a `BETWEEN-SERVERS-KEY`; no published licence for third-party automated access. |
| OpenSooq | `sa.opensooq.com` + Next.js SSR state | No English ToS found | **UNCLEAR (lean NO)** | **`Disallow: /api/*`, `/_next*`, `/ajax-api*`, `/ar/*`, `/en/*`** | **H** | VERIFIED | Client parses `/_next` SSR state — a disallowed path pattern. |
| Salla App Store | `api.salla.dev/marketplace/v2/*` | [Salla docs](https://docs.salla.dev/) | **UNCLEAR** | No path disallows for `/marketplace/v2` | **L–M** | VERIFIED | Public developer-marketplace API with official docs; no standalone terms for bulk harvesting. |
| Aqar | `sa.aqar.fm/{category}/{city}` (RSC) | No English ToS found | **UNCLEAR (lean NO)** | **`Disallow: /graphql`, `/search/`, `/view/`, and used category slugs** | **H** | VERIFIED | Client's target paths explicitly disallowed; also Cloudflare-403 to cloud IPs (WAF-blocked / gracefully degrading). |
| Syarah | `syarah.com/autos` (SSR) | No English ToS found | **UNCLEAR** | `Disallow: /api/`, `/*?*`; `/autos` allowed; two search endpoints explicitly allow-listed | **L–M** | VERIFIED | `/autos` crawlable; private `/api/` disallowed. |
| Sabbar | `sabbar.com/ar/jobs` | No ToS found | **UNCLEAR** | **`User-Agent: * Allow: /`** (fully crawl-allowed) | **L** | VERIFIED | Lowest-friction of the 12, but still no licence for commercial reuse. |
| Jarir (Constructor.io) | `ac.cnstrc.com/search/…` | Constructor terms not found; [jarir.com robots](https://www.jarir.com/robots.txt) | **UNCLEAR** | jarir.com disallows `/api/`, `/dp/*`; client hits a **separate** host | **M** | VERIFIED (robots) / INFERRED (terms) | Public frontend key reused from a backend — see §4. |
| eXtra (Unbxd) | `search.unbxd.io/{apiKey}/{siteKey}/search` | Unbxd terms not found; [extra.com robots](https://www.extra.com/robots.txt) | **UNCLEAR** | extra.com disallows `/search`; client hits a separate host | **M** | VERIFIED (robots) / INFERRED | Public Unbxd key reused from backend. |
| Etimad | `tenders.etimad.sa/Tender/AllSupplierTendersForVisitorAsync` | No ToS found (government platform) | **UNCLEAR** | `robots.txt` returns a **CAPTCHA / anti-bot challenge** | **M** | VERIFIED | Anti-bot gate signals automated access is discouraged; visitor endpoints reverse-engineered. |
| Kafiil | `kafiil.com/projects`, `/services` | No ToS found | **UNCLEAR** | Only register/login/purchase disallowed; `/projects`, `/services` **allowed** | **L–M** | VERIFIED | Paths crawlable; no licence or prohibition found. |
| Nice One | `niceonesa.com/ar/search?q=…` | No ToS found | **UNCLEAR (lean NO)** | **`Disallow: /search`**, `*?filters=*`, `*sort=*` — re-fetched, confirmed | **H** | VERIFIED | Client's exact `/ar/search?q=` path is robots-disallowed. |
| Golden Scent | `goldenscent.com/ar/search?q=…` | No ToS found | **UNCLEAR (lean NO)** | **`User-Agent: * Disallow: /`** (full disallow) + `/search` — re-fetched, confirmed | **H** | VERIFIED | Client sends a generic browser UA → falls under `*` → whole site disallowed. |
| Noon / LuLu | `noon.com/_svc/catalog/api/v3/u/search`; `gcc.luluhypermarket.com` | No ToS found | **UNCLEAR** | n/a | **M** | INFERRED | Noon documented as TLS/WAF-blocked (ClientHello fingerprinting), degrading gracefully. |

**WAF-blocked / gracefully-degrading** (documented in `DATA_EXPANSION_STUDY.md` §6): Noon, Aqar, Al-Dawaa, Sharaf DG, Amazon, and Reddit `.json`. `MarketplaceRegistry.run_health_check()` isolates each client and labels failures `UNAVAILABLE` — that is an **availability** behavior, **not** a compliance mitigation.

## 3. Top compliance risks, ranked

1. **Reddit (all tiers)** — `Disallow: /` for `*`, plus a robots.txt pointer to "research and non-commercial use" and Data API Terms §3.1/§3.2 requiring a commercial agreement. The agent's purpose is commercial product design and the README explicitly claims to bypass Reddit's 403 walls. Clearest breach.
2. **Google Autocomplete + Google Trends RSS** — Google ToS bars automated access in violation of robots.txt and reverse engineering; Autocomplete is an undocumented internal endpoint (`client=firefox`) with no licence. Trends RSS has no commercial grant — the same structural gap that got Google News disabled.
3. **Robots-disallowed paths actually hit** — OpenSooq (`/api/*`, `/_next*`), Aqar (`/graphql` + category slugs), Nice One (`/search`), Golden Scent (`*` full disallow + `/search`). Concrete path-level violations, not gray areas.
4. **Arctic Shift** — redistributes Reddit content with no licence of its own; cannot cure Reddit's commercial-use restriction, and exists to evade Reddit's access controls.
5. **Reused public search keys** — Constructor.io / Unbxd / Algolia keys embedded in Jarir/eXtra frontends are driven from a separate Cloudflare Worker/backend for systematic catalog extraction. A search-only key is *designed to be public* for frontend use, but the retailer's vendor contract governs that key; third-party backend harvesting is a different use than the licensed on-site search UI, and the retail hosts' `robots.txt` disallow `/api/` and `/search`.

## 4. Recommended actions (research only — no code changes proposed)

- **Gate behind opt-in flags (like `GOOGLE_NEWS_RSS_ENABLED`), default OFF:** Google Autocomplete, Google Trends RSS, all Reddit tiers + Arctic Shift, Product Hunt feed, and the four robots-disallowed clients (OpenSooq, Aqar, Nice One, Golden Scent). Personal-experimentation-only until licensed.
- **Lowest-risk to keep** (still UNCLEAR commercial rights — keep behind a flag or add attribution/rate-limit discipline): HN Algolia API, Sabbar (`Allow: /`), Syarah `/autos` + allow-listed endpoints, Kafiil, Salla marketplace API, Haraj. **Do not** label any source "compliant" merely because no prohibition was found.
- **Partner / licence conversations:** Reddit (commercial Data API / Public Content Policy), Google (official APIs), Product Hunt (official OAuth2 API), and the retailers whose Constructor.io / Unbxd / Algolia keys are reused — or replace those with each vendor's own licensed API.
- **Operational:** have the health check respect `robots.txt` per host rather than only recording `UNAVAILABLE`; stop spoofing browser UAs for disallowed hosts.

## 5. Coverage & limitations

The full **Product Hunt legal text** (403), **Reddit's Public Content Policy body** (403 — relied on the robots.txt pointer plus the verified Data API Terms), and any published ToS/API terms for the **Arabic-language marketplace sites** (Mostaql/Khamsat terms are Arabic, transactional, silent on automated collection), **Constructor.io**, **Unbxd**, **Arctic Shift**, **Etimad** (CAPTCHA-gated robots) and the **Salla marketplace API** could not be retrieved — those entries are INFERRED / UNCLEAR, not cleared. Several targets are login-, WAF- or geo-gated, so live behaviour may differ from the fetched `robots.txt`. Google News RSS was already handled and excluded.

**Independently re-fetched and confirmed by the coordinating agent:** `www.reddit.com/robots.txt` (`Disallow: /`), `trends.google.com/robots.txt` (only `/explore?` blocked), `goldenscent.com/robots.txt` (`User-Agent: * Disallow: /`), `niceonesa.com/robots.txt` (`Disallow: /search`).

---

*This audit covers source licensing only. It does not assess the project's own [MIT LICENSE](../LICENSE), which covers repository source code and grants no rights to third-party data.*
