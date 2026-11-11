# Data Expansion Study — How much more is extractable from the Saudi / GCC fleet?

**Date:** 2026-11-11
**Scope:** the 12 built clients, the 20-platform candidate fleet (`CANDIDATE_MARKETPLACES_FLEET.md`), and the free "demand signal" sources in `README.md`.
**Method:** 8 parallel research subagents, one per independent website cluster, each told to verify endpoints against **primary sources** (official API docs, the site's own JS/SSR payloads, live read-only GETs). Every finding is labelled **VERIFIED** (a source or live response was found) or **INFERRED** (reasoned from platform conventions). No credentials, cookies or tokens were captured or reproduced; no scraping was performed beyond single public read-only probes. This is a feasibility study, not a harvesting run.

---

## 1. Verdict

**Yes — there is substantially more data, an estimated 2–4× what the existing clients capture** (basis: the public discovery keys already in the Worker expose browse / facet / autocomplete / recommendation / PDP endpoints with several extra fields per SKU on top of today's single search call). But the study's main conclusion is that the constraint has *moved*:

> The project does **not** have an "endpoint discovery" problem. It has a **storage / identity** problem. Most of the untapped data sits behind public keys and endpoints the codebase **already holds**, or behind static sitemaps that need no auth at all. Adding a 13th or 30th scraper yields less marginal value than adding a time-series store and a barcode (EAN/GTIN) resolver.

There is also a hard ceiling on the original "as many APIs as possible" ambition: about **10 of the ~34 surfaces examined are partnership-gated** (OAuth contracts, affiliate accounts, seller credentials) and cannot be harvested by a free Worker at all.

---

## 2. Evidence quality — what was actually confirmed live

Concrete probes the agents ran (these are the strongest evidence in the study):

| Probe | Result | Consequence |
|---|---|---|
| `completion.amazon.sa/api/2017/suggestions?...` | **200, real JSON** (`suggestions[].value`, `responseId`) | Only genuinely free Amazon surface |
| `gcc.luluhypermarket.com/en-sa/list/?format=json` | **200, 11,843 SKUs / 593 pages**, facets, `ean`, `taxRate`, `isGlutenFree`, `stockCount` | Highest value/effort new dataset |
| Nahdi `/en-sa/plp/*` | **200, 699KB RSC payload** embedding real Algolia hits + config | Free, no WAF |
| `api.salla.dev/marketplace/v2/apps` | **200 anonymous JSON** | Zero-friction enrichment |
| `POST graphql.haraj.com.sa` | **200 `{"data":{"__typename":"Query"}}`** anonymous | Open GraphQL |
| Aqar / Syarah `sitemap.xml` children | **200 static XML**, robots-allowed | Free time-series |
| `saudi.sharafdg.com/wp-json/wc/store/v1/products` | **403 (WAF)** | Must use Algolia key instead |
| `al-dawaa.com` homepage + OCC API | **403 Cloudflare "Attention Required!"** even with browser UA | **Contradicts fleet doc** (see §4) |
| `alsaifgallery.com/graphql` via GET | **404** (POST-only / CDN) | Expected, not a blocker |
| `reddit.com/r/.../new.json` | **403** | Arctic Shift remains the path |
| Google Trends `/api/explore` + Books API | **429 / 404** | Exclude from free cron |

Platform mechanisms (Magento GraphQL schema, SAP OCC v2, Spree Storefront, Algolia REST, WooCommerce Store API, SFCC controllers, Constructor.io, Unbxd, ZATCA) were verified against **official vendor documentation**; site-specific field presence, index names and base-site IDs remain INFERRED.

---

## 3. The five cross-cutting findings

### Finding 1 — The biggest untapped data is behind keys we already hold
The `cloudflare-worker/src/index.ts` already stores public Jarir (Constructor.io), eXtra (Unbxd) and Noon keys. Each vendor's *other* endpoints multiply yield with **zero new credentials and zero new infra**:

- **Jarir / Constructor.io**: `/browse/{facet}/{value}`, `fmt_options.show_hidden_fields` (exposes `inventory_count`, `store_availability`), `variations_map`, `/v1/autocomplete/`, `/v1/recommendations` (best-sellers, bought-together), `lang=ar` bilingual, facet-option counts. VERIFIED `security: []` = no auth on search/browse. [Constructor.io docs](https://docs.constructor.com/reference/v1-search-get-search-results)
- **eXtra / Unbxd**: `/category` (facet counts + `stats=price` min/max + `variants=true`), `/autosuggest` (`topQueries`, `trendingSearches`, `keywordSuggestions` — a **direct demand signal**), `didYouMean`. [Unbxd docs](https://docs.netcoreunbxd.com/docs/search-api)
- **Noon**: the undocumented PDP object `/_svc/catalog/api/v3/u/{ZSKU}/p/` returns feature bullets, variants, media, MRP, specs/EAN in one GET — completely missed by the search-only client (TLS fingerprinting makes this PARTIAL/risky from a Worker).

The same pattern repeats on the candidate side: **Tamimi uses Constructor.io** (same stack as Jarir, near-zero marginal engineering), **Danube, Nahdi, Sharaf DG and Sun & Sand Sports expose public Algolia search-only keys**, and **three electronics retailers (Alsaif, Eddy, Black Box) share one unauthenticated Magento2 `POST /graphql` schema** (`custom_attributesV2` spec dictionaries, `aggregations`, related/upsell/crosssell graphs, `sa_ar`/`sa_en` dual store views).

### Finding 2 — Sitemaps are the universal free fallback, and they unlock the missing history layer
The earlier 8.7/10 project review named **"no persistent unified data storage / price history"** as gap #1. Three sites leak exactly the raw material for it through robots-allowed static XML:

- **Haraj**: hourly partitioned sitemaps (`sitemapfiles.haraj.com.sa/YYYY-MM-DD/sitemap-*-HH.txt`) plus `postDate`/`updateDate`/`before_update_date` cursors → listing birth, refresh, relist, death events.
- **Aqar**: date-partitioned sale/rent sitemaps **2024-02 → 2026-11** with `<lastmod>`, plus `city/district/filter/price/{id}.xml` hub IDs → cohort, seasonal and price-drop proxies. Detail pages are Cloudflare-403 to cloud IPs, but the sitemaps are not.
- **Syarah**: `cardetail`, `prices`, `make_model_year` sitemaps and a `cars-by-ids` (100 IDs) re-poll → clean per-car price history. `/api/syarah_v1/` is 401 token-gated, sitemaps are open.

This is the cheapest possible route to the project's single biggest structural gap: **no auth, no keys, no WAF, plain `GET` + parse into D1/SQLite.**

### Finding 3 — The real ceiling is partnership, not scraping
A clean three-way split emerged. "More APIs" is bounded by credentials, not by cleverness:

| Tier | Platforms | Access |
|---|---|---|
| **Free / anonymous** (Worker-viable) | LuLu, Danube, Tamimi, Panda, Nahdi, **Whites (new)**, Alsaif, Eddy, Black Box, Sharaf DG (via Algolia), Namshi, Sun & Sand Sports, Haraj, Aqar/Syarah sitemaps, Sabbar, Kafiil, Salla App Store, Etimad visitor, Mostaql, Khamsat, Amazon completion, all free signal sources | plain HTTP / public keys |
| **Partial / conditional** | Carrefour (geo + BFF), Noon PDP (TLS), Virgin OCC (guest token + baseSiteId), OpenSooq (HMAC device handshake), Jahez consumer pages | needs extra posture |
| **Partner-gated** (no free path) | Zid (`X-Manager-Token` + OAuth, 60 rpm), Salla merchant/partner APIs, Jahez `integration-api`, Ounass (Partnerize), Boutiqaat (Admitad/ArabClicks), Sivvi / Noon Partner API, Amazon deep catalog, Product Hunt GraphQL, X API | **approved account required** |

*Evidence caveat:* only the 11 live probes in §2 are **VERIFIED** at the HTTP level. Most tier placements are **INFERRED** from vendor docs and platform conventions — the Alsaif/Eddy/Black Box Magento `POST /graphql`, Tamimi's Constructor key and the Algolia index names were not confirmed live. Treat the tier column as a routing hypothesis: run one read-only probe per site before committing engineering time.

Notable: **Amazon PA-API 5 is deprecated (HTTP 403 `AccessDeniedException`)** and the replacement Creators API needs credentials **plus 10 qualifying sales / 30 days** — so the fleet doc's "autocomplete only" recommendation is correct and deep Amazon catalog is not a free target. [Amazon Creators API](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction)

### Finding 4 — Demand signals are a parsing change, not a new integration
The richest untapped signal data is **already inside endpoints the daily cron calls**; it is simply discarded:

- **Google Trends SA RSS**: `ht:approx_traffic` (numeric magnitude, e.g. "2000+"), `pubDate` trend-start, and up to 3 `ht:news_item` links — currently only titles are kept. Daily snapshots → slope + anomaly detection. [RSS](https://trends.google.com/trending/rss?geo=SA)
- **HN Algolia**: `nbHits` (e.g. 14,469 for "salla"), `points`, `num_comments`, `created_at_i`, `numericFilters` → demand magnitude and time-series slope. [HN Algolia API](https://hn.algolia.com/api)
- **Arctic Shift**: full Reddit objects (`score`, `upvote_ratio`, `num_comments`, **author flair = region/city** 🇸🇦, `created_utc`, crosspost graph) instead of text-only RSS. [Arctic Shift](https://github.com/ArthurHeitmann/arctic_shift)
- **Genuinely new free sources**: GitHub REST search (`total_count` 734 repos for "zatca", stars, topics), Stack Exchange API (`view_count`, `score`, `is_answered`), iTunes-SA review RSS (Arabic review text + `im:rating` sentiment), Wikipedia Pageviews. All no-key, rate-limited.

The two highest-value "full" sources are **excluded** from a free cron: Google Trends `/api/explore` (**unofficial, cookie/token handshake, aggressive 429 — we observed 429 here**, so too fragile for an unattended cron) and X/Twitter (free tier discontinued Feb 2026). [pytrends post-mortem](https://apiserpent.com/blog/pytrends-dead-google-trends-data-2026)

### Finding 5 — The bottleneck is identity resolution, not coverage
Every cluster independently surfaced **EAN/GTIN/MPN**: LuLu `ean`/`mainEan`, Carrefour GTIN, Al-Dawaa OCC barcodes, Zid product `barcode`, Magento `custom_attributesV2` MPN/GTIN, Ounass style codes, Namshi `parentSku`. Cross-store price comparison — the project's stated commercial purpose — is impossible without a resolver that links those identifiers. This converges exactly with the earlier review's gap #3 ("universal barcode matching"). **The study's recommendation is therefore to build the resolver and the history store before adding more scrapers.**

---

## 4. Corrections to existing documentation

These are the highest-value outputs of the study, because they prevent building on wrong assumptions:

1. **Al-Dawaa is NOT free-Worker-viable.** `CANDIDATE_MARKETPLACES_FLEET.md` ranks it **#1 (8.2/10, "Yes (OCC v2 REST)")**. Live probes returned **Cloudflare 403 on both homepage and OCC API** from a datacenter IP even with browser UA/Referer/Origin. It needs browser-render/TLS impersonation + an anonymous OAuth2 guest token. **Nahdi and Whites** (Next.js + public Algolia SSR payload, no WAF) are the actual easy pharmacy wins.
2. **"15% VAT" is not universal.** ZATCA zero-rates *SFDA/MoH-classified "qualifying medicines"*, **not** a clean Rx/OTC split — so a per-SKU derivation is required. The LuLu `?format=json` sample returned `taxRate: 5` (field semantics unclear — Saudi statutory rates are 0% / 15%, so this is likely a legacy or category code, not a percent); do not use it as VAT ground truth. Treat the fleet doc's VAT line as a simplification, not ground truth. [ZATCA retail VAT guideline](https://zatca.gov.sa/en/HelpCenter/guidelines/Documents/Guideline-For-Retail-Sector-under-VAT-Provisions.pdf)
3. **Amazon PA-API 5 is dead** (403); the fleet doc's autocomplete-only path stands, but any "deep catalog via PA-API" plan must be dropped.
4. **Aqar / Syarah / OpenSooq** detail APIs are gated (403 / 401 / HMAC handshake), but their sitemaps and robots-disclosed paths are free — the fleet doc understates what is harvestable from them.

---

## 5. Priority roadmap

**Tier 1 — near-zero cost, do first (all free, keys already in hand or plain GET)**
1. Extend Constructor.io, Unbxd and Noon clients with `browse`/`facets`/`autosuggest`/`recommendations`/PDP calls (roughly 2–4× the fields per SKU, no new infra).
2. Harvest Haraj hourly + Aqar date-partitioned + Syarah `cardetail`/`prices` sitemaps into a time-series store (D1 or SQLite).
3. Parse the discarded numeric fields from Trends RSS, HN Algolia and Arctic Shift in `agent.py`.
4. Add the three Magento2 `/graphql` stores (Alsaif, Eddy, Black Box) with one shared schema adapter, plus Tamimi (Constructor) and Danube/Nahdi/Whites (Algolia).

**Tier 2 — moderate effort**
5. Etimad **award results** endpoint (winning bidder, all bidder prices, awarded value — **INFERRED** from third-party API specs plus Etimad's public visitor endpoints, not live-probed here). Single highest-leverage new dataset if confirmed.
6. Sabbar salary-band matrix, Kafiil/Mostaql bid-count + budget series, Salla App Store review histograms, Panda weekly leaflets + loyalty pricing, Carrefour geo-scoped branch stock.
7. EAN/GTIN cross-store resolver — the prerequisite for real price comparison.

**Tier 3 — partnership required (park, don't engineer)**
8. Zid / Salla merchant APIs / Jahez B2B / Noon Partner / Partnerize / Admitad — pursue only if a partner account is obtained. Amazon deep catalog and X/Twitter should be excluded from a free-only cron entirely.

---

## 6. Caveats & boundaries

- **VERIFIED vs INFERRED**: vendor mechanisms are well-sourced; site-specific field presence, Algolia app IDs / index names, SAP `baseSiteId`s and internal REST paths are **INFERRED** and must be confirmed by one live probe before implementation.
- **Terms of use**: Google News RSS is licensed for "personal, non-commercial use"; OpenSooq `robots.txt` disallows `/api/*`; several affiliate programs are login-gated. Respect robots, ToS and rate limits. No cookies, tokens or HAR contents belong in the repo.
- **TLS / WAF reality**: Noon (ClientHello fingerprinting), Al-Dawaa (Cloudflare), Sharaf DG `/wp-json` (403), Aqar (403 to cloud IPs) and Amazon (AWS WAF) will not yield to a plain Worker `fetch`; `curl_cffi`-style browser impersonation or residential proxies are required. That is the one place where "free" has a real cost.
- **Scope**: this is a feasibility/desktop study. It did not run `reverse-api-engineer` browser captures, generate clients, or modify any code. Endpoint names here are *targets*, not confirmed-working integrations.

---

## 7. Key primary sources

**Vendor / platform docs** — [Adobe Commerce GraphQL products](https://developer.adobe.com/commerce/webapi/graphql/schema/products/queries/products) · [SAP OCC v2 REST (SAP Help, Telco Accelerator reference)](https://help.sap.com/docs/TELCO_ACCELERATOR/620a19f591cf4846a0160c74754c43b2.html) · [Spree Storefront API](https://spreecommerce.org/docs/api-reference/storefront/products/list-all-products) · [Algolia REST search](https://algolia.com/doc/rest-api/search/search) · [WooCommerce Store API](https://developer.woocommerce.com/docs/apis/store-api/resources-endpoints/products/) · [SFCC dw.catalog Product](https://salesforcecommercecloud.github.io/b2c-dev-doc/) · [Constructor.io](https://docs.constructor.com/reference/v1-search-get-search-results) · [Unbxd](https://docs.netcoreunbxd.com/docs/search-api) · [Salla docs](https://docs.salla.dev/authorization) · [Zid docs](https://docs.zid.sa/authorization) · [Strapi REST](https://docs.strapi.io/cms/api/rest)

**Regulatory / open data** — [ZATCA VAT retail guideline](https://zatca.gov.sa/en/HelpCenter/guidelines/Documents/Guideline-For-Retail-Sector-under-VAT-Provisions.pdf) · [SASO energy efficiency labels](https://saso.gov.sa/en/sectors/certificates/efficiency_card/Pages/default.aspx) · [REGA real-estate indicator](https://rei.rega.gov.sa/en) · [GASTAT](https://www.stats.gov.sa/en/) · [Saudi open data portal](https://open.data.gov.sa/)

**Signals** — [Google Trends SA RSS](https://trends.google.com/trending/rss?geo=SA) · [HN Algolia API](https://hn.algolia.com/api) · [Arctic Shift](https://github.com/ArthurHeitmann/arctic_shift) · [GitHub REST search](https://docs.github.com/en/rest/search) · [Stack Exchange API](https://api.stackexchange.com/) · [Etimad developer portal](https://apiportal.etimad.sa/en/get-started)
