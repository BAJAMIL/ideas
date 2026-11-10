# Saudi & GCC E-Commerce Marketplace Intelligence Fleet (Candidate Registry)

This registry tracks the technical evaluation of 20 high-value e-commerce and retail candidates across Saudi Arabia (KSA) and the GCC, researched in parallel by dedicated AI subagents.

---

## Evaluation Criteria
1. **Search & Discovery API:** Dedicated REST/GraphQL, search provider (Algolia, Constructor, Unbxd, Bloomreach, Elastic), or Nuxt/Next SSR JSON.
2. **Data Richness:** Structured SKU, title (AR/EN), SAR pricing, VAT transparency (15%), discounts, stock/availability, brand, and media assets.
3. **Anti-Bot Posture:** Cloudflare Turnstile/WAF, Akamai Bot Manager, Datadome, or open edge API.
4. **Proxy Dependency:** Can it be harvested using 100% free Cloudflare Workers / direct HTTP, or does it require paid residential proxies?
5. **Integration Score:** Rated 1 to 10 based on ease of integration and data yield.

---

## Candidate Fleet Evaluation Matrix

| # | Platform | Primary Vertical | Tech / Search Engine | Anti-Bot Level | Free Worker Viable? | Score / 10 | Status |
|:---|:---|:---|:---|:---|:---:|:---:|:---:|
| 1 | **Jahez KSA** | Food & Quick-Commerce (PIK) | REST / OAuth 2.0 B2B (`integration-api.jahez.net`) | High (Cloudflare WAF on app) | Partner: Yes / Public: Hard | **7.4 / 10** | **Evaluated** |
| 2 | **Amazon SA** | General Retail, Tech & Books | Amazon A9 / HTML / Open Autocomplete | Very High (AWS WAF / Captcha) | Autocomplete: Yes / Catalog: Proxy | **6.5 / 10** | **Evaluated** |
| 3 | **Lulu Hypermarket** | Grocery & Department Store | Akinon Commerce / Elasticsearch (`?format=json`) | Moderate / High (Cloudflare) | Yes (via `?format=json`) | **6.8 / 10** | **Evaluated** |
| 4 | **Panda / Panda Click** | Hypermarket & Groceries | Next.js SSR + Strapi CMS + ToDoorstep APIs | Moderate (Cloudflare WAF) | **Yes (Next.js / REST)** | **7.1 / 10** | **Evaluated** |
| 5 | **Danube / BinDawood** | Premium Grocery & Imports | Spree Commerce / Algolia Client API | Moderate (Cloudflare) | **Yes (Direct Algolia)** | **7.5 / 10** | **Evaluated** |
| 6 | **Carrefour KSA** | Hypermarket & Electronics | MAF Retail BFF / Algolia | High (Akamai + DataDome) | Partial (Requires TLS/BFF) | **6.2 / 10** | **Evaluated** |
| 7 | **Tamimi Markets** | Specialty Groceries | ZopSmart Headless REST / GCS Assets | Low / Moderate | **Yes (Direct REST API)** | **7.6 / 10** | **Evaluated** |
| 8 | **Virgin Megastore** | Gaming, Tech, Books & Culture | SAP Commerce Cloud (OCC v2) / Solr | High (Akamai Bot Manager) | Direct OCC (with headers) | **6.8 / 10** | **Evaluated** |
| 9 | **Sharaf DG KSA** | Electronics & Appliances | Enterprise WooCommerce + Algolia InstantSearch | Moderate (Cloudflare CDN) | **Yes (Algolia Facets / REST)** | **7.4 / 10** | **Evaluated** |
| 10 | **Black Box KSA** | Consumer Electronics & TV | Headless Magento 2 / GraphQL | Moderate (Cloudflare WAF) | **Yes (Direct GraphQL)** | **7.0 / 10** | **Evaluated** |
| 11 | **Eddy Electronics** | Furniture, Appliances & Tech | Magento 2 GraphQL (`/graphql`) | Moderate (AWS WAF / CloudFront) | Yes (via GraphQL) | **7.8 / 10** | **Evaluated** |
| 12 | **Alsaif Gallery** | Kitchenware & Small Appliances | Magento 2 GraphQL (`/graphql`) | Moderate (Cloudflare WAF) | **Yes (Direct GraphQL)** | **8.0 / 10** | **Evaluated** |
| 13 | **Nahdi Pharmacy** | Healthcare & Baby Care | Adobe Commerce / **Algolia Client API** | Moderate (AWS WAF) | **Yes (Direct Algolia)** | **6.4 / 10** *(7.8 Search)* | **Evaluated** |
| 14 | **Al-Dawaa Pharmacies**| Health, OTC & Dermacosmetics | SAP Commerce Cloud (OCC v2) / Solr | Moderate / High (Geo-WAF) | **Yes (OCC v2 REST)** | **8.2 / 10** | **Evaluated** |
| 15 | **Namshi KSA** | Fashion, Apparel & Shoes | REST Gateway (`api.namshi.com`) | Moderate (Cloudflare Bot) | **Yes (REST Gateway)** | **8.0 / 10** | **Evaluated** |
| 16 | **Sivvi KSA** | Fashion & Beauty | Noon Catalog API (`noon.partners`) | Moderate (Cloudflare WAF) | Yes (via Noon API) | **7.2 / 10** | **Evaluated** |
| 17 | **Ounass KSA** | Luxury Designer & Regional Fashion | Node.js Headless / Algolia / Partnerize | Very High (Cloudflare + Kasada) | Partnerize Feeds: Yes | **7.6 / 10** | **Evaluated** |
| 18 | **Sun & Sand Sports** | Sports & Athletic Apparel | Salesforce Commerce Cloud (SFCC) / Algolia | Moderate / High (Akamai/SFCC) | **Yes (SFCC Search / Algolia)** | **7.8 / 10** | **Evaluated** |
| 19 | **Zid Ecosystem** | Saudi Merchant Stores | Zid Multi-Tenant API (`api.zid.sa/v1/`) | Moderate (OAuth2 / Dual Token) | Yes (Partner/Merchant) | **7.7 / 10** | **Evaluated** |
| 20 | **Boutiqaat KSA** | Beauty, Perfume & Influencers | Magento 2 / GraphQL / Affiliate | High (Cloudflare Enterprise) | Affiliate Feeds: Yes | **4.5 / 10** | **Evaluated** |

---

## Detailed Platform Profiles

### 1. Jahez KSA (`jahez.com` / `jahez.net`)
* **Domains:** `jahez.com`, `jahez.net`, `integration-portal.jahez.net`, `integration-api.jahez.net`
* **Architecture:** Dual API: Official B2B Partner API with OAuth 2.0 for POS/ERP (`Foodics`, `Deliverect`, `Odoo`), and mobile client APIs (`api.jahez.net`).
* **Coverage:** Pan-KSA covering all Tier-1 and 50+ Tier-2 cities.
* **PIK Retail:** Extends delivery radius up to 100km for non-food retail (electronics, beauty, gifts).
* **SAR Pricing & Tax:** 15% VAT explicitly segmented; delivery fee SAR 10–20; Jahez Prime gives free delivery on orders >= SAR 35.
* **Anti-Bot & Security:** Cloudflare WAF, geo-fenced coordinates, SSL pinning on mobile app.
* **Recommendation:** Integrate via official B2B integration credentials (`integration@jahez.net`) or POS middleware for 100% reliable real-time menu and order feeds.

### 2. Zid Ecosystem (`zid.sa` / `mazeed.sa`)
* **Domains:** `zid.sa`, `docs.zid.sa`, `apps.zid.sa`, `mazeed.sa`
* **Scale:** 10,000+ active Saudi/GCC enterprise and high-AOV DTC brands (perfumes, abayas, specialty coffee, luxury retail).
* **Consumer Marketplace:** `mazeed.sa` acts as Zid's unified multi-store consumer marketplace.
* **API Architecture:** RESTful multi-tenant API at `https://api.zid.sa/v1/` with OAuth 2.0 Authorization Code grant.
* **Authorization Headers:** Unique dual-token requirement: `Authorization: Bearer <access_token>` plus `X-Manager-Token: <manager_token>`.
* **Rate Limits:** 60 requests/minute per store (Leaky Bucket algorithm). Webhook-first architecture (`order.create`, `product.update`, `inventory.update`) is mandatory.
* **Tax & ZATCA:** Explicit 15% KSA VAT, HS code support, and Phase-2 e-invoicing compliance.
* **Recommendation:** Integrate as a registered App Market public app (`apps.zid.sa`) to unlock all 10,000+ merchants without requiring store-level Pro/Enterprise custom API surcharges.

### 3. Amazon Saudi Arabia (`amazon.sa`)
* **Domain:** `https://www.amazon.sa` (Marketplace ID: `A17E79C6D8DWNP`)
* **Open Autocomplete API:** Completely unauthenticated live keyword and category recommendation API at `https://completion.amazon.sa/api/2017/suggestions?mid=A17E79C6D8DWNP&alias=aps&prefix={query}&lop=en_AE`.
* **Search Architecture:** `/s?k={query}&page={page}&s={sort}&rh={filters}` with ASIN extraction via `div[data-component-type="s-search-result"]`.
* **Pricing & Locale:** Strict SAR pricing (`lc-main=en_AE; i18n-prefs=SAR;`).
* **Anti-Bot Defense:** Heavy AWS WAF / CloudFront bot detection and CAPTCHA walls on raw datacenter IPs.
* **Recommendation:** Use open Autocomplete API for free zero-proxy keyword intelligence, and route deep catalog queries through managed SERP/proxy scraping.

### 4. Carrefour Saudi Arabia (`carrefourksa.com`)
* **Operator:** Majid Al Futtaim (MAF) Retail (territory code `mafsau`).
* **API Architecture:** High-performance REST Backend-For-Frontend (`https://www.carrefourksa.com/api/v4/search` and `/api/v8/categories/{id}`).
* **Search Provider:** Algolia Cloud cluster powering instant search suggestions and facet filtering behind MAF BFF.
* **Pricing & Tax:** Native SAR pricing with 15% VAT included.
* **Inventory Dependency:** Strict geolocation requirements (`latitude`, `longitude`, and `areaCode` e.g., Riyadh, Jeddah) for accurate grocery stock.
* **Anti-Bot Defense:** Akamai Bot Manager + DataDome. Requires browser TLS fingerprints (`curl-cffi`) and residential/GCC IPs.

### 5. Virgin Megastore Saudi Arabia (`virginmegastore.sa`)
* **Platform:** SAP Commerce Cloud (Hybris CCv2) + Apache Solr + Bloomreach Discovery.
* **API Endpoints:** Standard SAP OCC v2 REST endpoints (`/occ/v2/{baseSiteId}/products/search` and `/occ/v2/{baseSiteId}/products/suggestions`).
* **Key Categories:** Gaming (PS5, Xbox, PC Gaming, Razer, Logitech), Books (Arabic/English, Manga), Gadgets/Audio (Sony, Bose, Marshall, Funko Pop).
* **Tax & Pricing:** Standard SAR with mandatory 15% VAT; Mada, Apple Pay, Tabby, and Tamara.
* **Anti-Bot Defense:** Guarded by Akamai Bot Manager / Edge Defender. Direct OCC querying requires browser TLS impersonation and valid guest session tokens.

### 6. Eddy Home & Electronics (`eddy.com.sa`)
* **Platform:** Adobe Commerce (Magento 2 Enterprise) on AWS multi-AZ, managed by SnapTec.
* **Direct GraphQL API:** `https://eddy.com.sa/graphql` (Supports standard `products(...)` query with full JSON specs, prices, and stock).
* **REST & Autocomplete:** `/rest/V1/` and `/catalogsearch/ajax/suggest`.
* **Catalog Pillars:** Major Appliances (Refrigerators, Washers, ACs with SASO ratings), Consumer Electronics (Smart TVs, Mobiles, Computing, Gaming), and Furniture (Living, Bedroom, Dining).
* **Financing:** Tabby, Tamara BNPL, and 0% bank installment plans across major Saudi banks.
* **Recommendation:** Highest feasibility for consumer tech and appliances; query the `/graphql` endpoint directly.

### 7. Ounass Luxury Saudi Arabia (`saudi.ounass.com`)
* **Operator:** Al Tayer Digital (Dubai / Riyadh).
* **Catalog:** Tier-1 luxury houses (Gucci, Prada, Saint Laurent, Balenciaga), niche perfumery (Amouage, Parfums de Marly), and regional Saudi designers (modest fashion, abayas, luxury Arabic sandals).
* **Pricing:** SAR with 15% ZATCA VAT and 100% DDP (Delivered Duty Paid) cross-border customs coverage.
* **Integration Routes:** Primary recommended route via official **Partnerize product data feeds (CSV, XML, JSON)** with 30-day attribution. Raw scraping is heavily restricted by Cloudflare Enterprise + Kasada.

### 8. Boutiqaat KSA / GCC (`boutiqaat.com`)
* **Model:** Influencer-led social e-commerce featuring 700+ celebrity digital boutiques (Fouz Al Fahad, Noha Nabil, Dr. Kholoud).
* **Catalog Strengths:** Rare Gulf perfumery (Gissah, Atyab Al Marshoud, Arabian Oud), international niche beauty, and cosmetics.
* **Platform:** Magento 2 Enterprise + Next.js + Algolia search.
* **Anti-Bot:** Cloudflare Enterprise WAF.
* **Integration Route:** Closed 1P supplier model; external catalog feeds best consumed via regional affiliate networks (Admitad / ArabClicks).

### 9. Danube KSA / BinDawood (`danube.sa`)
* **Operator:** BinDawood Holding (Tadawul: 4161) / IACo.
* **Platform:** Spree Commerce (Ruby on Rails) + LitElement Web Components PWA.
* **Direct Search API:** **Algolia** (`algoliasearch` with public Search-Only client key).
* **Catalog Data Yield:** Product ID, barcode/EAN, bilingual titles (`name_en`, `name_ar`), taxons, prices in SAR, 15% VAT, and Amazon CloudFront packshot images.
* **Store Localization:** Inventory availability is tied to local branch / city coordinates (`supermarket_id`).
* **Recommendation:** **Grade A (9.0/10 for Catalog & Search Discovery)**. Direct Algolia queries completely bypass web scraping barriers and Cloudflare WAF with zero proxy cost.

### 10. Alsaif Gallery KSA (`alsaifgallery.com`)
* **Company:** Leading Saudi listed houseware retailer (Tadawul: 4192) with 60+ megastores.
* **Platform:** Decoupled **Adobe Commerce (Magento 2)** + Headless Next.js (NOT Salla!).
* **Direct GraphQL Endpoint:** `POST https://alsaifgallery.com/graphql` (Store: `sa_ar` or `sa_en`).
* **Flagship Brand:** **Edison (إديسون)** appliances (pressure cookers, air fryers, stand mixers, Arabic bread bakers).
* **Pricing & Offers:** 15% VAT included, regular vs final discount prices, Tabby, Tamara BNPL.
* **Recommendation:** **High Feasibility (8.0/10)**. Querying the `/graphql` endpoint yields clean JSON without parsing messy HTML.

### 11. Namshi Saudi Arabia (`saudi.namshi.com`)
* **Operator:** Noon Group (acquired for $335M).
* **Scale:** 100,000+ active fashion SKUs, 2,000+ brands (Nike, Mango, Aldo, Ella, Amouage).
* **REST Gateway:** `https://api.namshi.com/catalog/search?q={query}` and `/catalog/products/{sku}`.
* **Mandatory Headers:** `X-Country: SA`, `X-Language: en|ar`, mobile `User-Agent`.
* **Media & Logistics:** Media hosted on Noon CDN (`f.nooncdn.com`), fulfillment via Noon Express.
* **Pricing & Tax:** 15% ZATCA VAT compliant gross pricing in SAR, Tabby/Tamara BNPL.
* **Recommendation:** **Grade A- (8.0/10)**. Standard REST JSON endpoints are highly accessible via mobile client header emulation.

### 12. Sivvi KSA (`sivvi.com/saudi-en`)
* **Platform:** Fast-fashion vertical of Noon AD Holdings.
* **Integration Channel:** Standardized under **Noon Partner API** (`noon.partners` / `api.noon.com` with `Contract: SA`).
* **Catalog:** High-street fashion, athleisure, and cosmetics sharing Noon PIM catalog taxonomy.
* **Fulfillment:** Same-day and sub-3-hour delivery in Riyadh via Noon Express & Noon Minutes.
* **Recommendation:** Integrate via Noon Partner API alongside Noon marketplace catalog feeds.

### 13. Black Box KSA (`blackbox.com.sa`)
* **Company:** Saudi omnichannel white-goods and consumer electronics retailer.
* **Platform:** Headless Adobe Commerce (Magento 2) + Next.js frontend (`store.ops.blackbox.com.sa`).
* **Direct API:** Magento GraphQL endpoint (`https://blackbox.com.sa/graphql`) and REST `/rest/V1/products`.
* **Catalog Coverage:** Daikin, Gree, LG, Samsung split ACs, home theater OLEDs, laptops, and refrigerators.
* **Pricing & Tax:** 15% ZATCA VAT included in SAR, Tabby and Tamara 4-split BNPL.
* **Recommendation:** **Feasible (7.0/10)**. Intercepting GraphQL queries yields structured JSON with specs and stock status.

### 14. Nahdi Pharmacy Online (`nahdionline.com`)
* **Company:** Saudi Arabia's #1 pharmacy chain (1,100+ stores).
* **Search Engine:** **Algolia DSN** (`window.algoliaConfig` with public search-only API keys).
* **Direct Search API:** `https://{APPLICATION_ID}-dsn.algolia.net/1/indexes/{INDEX_NAME}/queries`.
* **Catalog:** 25,000–35,000 SKUs (OTC analgesics, diabetes monitors, vitamins, baby formula, dermacosmetics).
* **Dual VAT Structure:** SFDA regulated drugs (0% VAT, fixed pricing), OTC & wellness (15% VAT included).
* **Recommendation:** **Grade A (7.8/10 for Catalog & Search Aggregation)**. Direct Algolia queries bypass AWS WAF and CloudFront with sub-50ms latency.

### 15. Al-Dawaa Pharmacies KSA (`al-dawaa.com`)
* **Company:** Tadawul: 4163. Over 975+ pharmacies, 23+ dark stores across KSA. FY25 Revenue: SAR 6.74 Billion.
* **Platform:** **SAP Commerce Cloud (Hybris)** + Headless Angular Spartacus SPA.
* **Core API:** SAP Omni Commerce Connect (**OCC v2 REST API**) under `https://api.al-dawaa.com/occ/v2/aldawaa/products/search`.
* **Search Engine:** **Apache Solr** with bilingual Arabic/English analyzers and SFDA medication code indexing.
* **Catalog Depth:** 25,000–35,000 SKUs covering healthcare, French dermacosmetics (La Roche-Posay, CeraVe, Vichy), infant nutrition, and diagnostic devices.
* **Recommendation:** **Grade A- (8.2/10)**. High-fidelity SAP OCC v2 REST endpoints return clean JSON with EAN barcodes and live store availability.

### 16. LuLu Hypermarket KSA (`luluhypermarket.com/en-sa`)
* **Platform:** Headless React SPA powered by **Akinon Commerce Cloud (ACC)** + **SAP Commerce Cloud (Hybris)**.
* **Direct JSON Flag:** `GET https://www.luluhypermarket.com/en-sa/list/?search_text={q}&format=json` (returns structured JSON containing pagination, facet aggregations, EAN barcodes, and product objects).
* **Search & Autocomplete:** Elasticsearch via Akinon (`/en-sa/autocomplete/?search_text={prefix}`).
* **URL Hierarchy:** Department URLs (`/en-sa/{category-slug}/c/{categoryCode}`) and PDP URLs (`/p/{sku-code}/`).
* **Pricing & Tax:** 15% VAT included in SAR (`vatRate: 15.0`), retail vs selling discount prices.
* **Recommendation:** **Solid B+ (6.8/10)**. Clean Akinon `format=json` catalog payloads make extraction fast when paired with Cloudflare TLS headers.

### 17. Sun & Sand Sports KSA (`en-sa.sssports.com`)
* **Operator:** Gulf Marketing Group (GMG). Largest sports retailer in the Middle East.
* **Platform:** **Salesforce Commerce Cloud (SFCC / B2C Commerce)** + Storefront Reference Architecture (SFRA).
* **Search Engine:** **Algolia AI Search** integrated client-side with SFCC for typeahead autocompletion, instant search, and facet filtering.
* **Core Endpoints:**
  * SFCC Search Controller: `https://en-sa.sssports.com/on/demandware.store/Sites-en-sa-Site/default/Search-Show?q={query}`
  * Product Detail Controller: `https://en-sa.sssports.com/on/demandware.store/Sites-en-sa-Site/default/Product-Show?pid={pid}`
  * Suggestions: `Search-GetSuggestions`
* **Enterprise Layer:** Akeneo PIM for multilingual product attributes, Fluent Commerce for OMS / click & collect, SAP S/4HANA ERP.
* **Tax & Currency:** All prices in SAR with 15% ZATCA VAT included. Supported by Tabby/Tamara BNPL, Apple Pay, Mada.
* **Anti-Bot & Infrastructure:** Akamai Edge Defender / SFCC DDoS shield. Product pages follow clean slug patterns: `en-sa.sssports.com/<slug>/<sku>.html`.
* **Recommendation:** **High Feasibility (7.8/10)**. SFCC search controllers and Algolia client requests can be queried directly with standard browser headers.

### 18. Panda / Panda Click KSA (`panda.sa` / `panda.com.sa`)
* **Operator:** Panda Retail Company (Savola Group). Largest grocery & hypermarket network in Saudi Arabia (200+ stores).
* **Frontend Architecture:** **Next.js (React)** with Server-Side Rendering (SSR) under `https://panda.sa/en/` and `https://panda.sa/ar/`.
* **Backend & Mobile Ecosystem:** Headless microservices (Node.js/NestJS), Strapi CMS for marketing, and legacy **ToDoorstep** app fulfillment APIs (`todoorstep.com` / `com.todoorstep.store`).
* **CDN & Asset Pipeline:**
  * Product Packshots: `https://images.todoorstep.com/product/{SKU_ID}/En.jpg` and `/Ar.jpg`
  * Next.js Image Optimization: `_next/image`
* **Coverage:** Nationwide grocery delivery spanning 20+ Saudi cities (Riyadh, Jeddah, Makkah, Madinah, Dammam, Khobar, Tabuk, Abha).
* **Pricing & Tax:** Strict SAR pricing with 15% VAT included. Weekly flyer promos and bundle discounts updated every Wednesday.
* **Recommendation:** **Grade B+ (7.1/10)**. Can be queried via Next.js SSR hydration data props (`__NEXT_DATA__`) or by directly querying the ToDoorstep catalog CDN by SKU.

### 19. Tamimi Markets KSA (`shop.tamimimarkets.com`)
* **Operator:** Tamimi Group. Saudi Arabia's premier upscale fresh foods and imported supermarket chain.
* **E-Commerce Platform:** **ZopSmart (SmartStore)** omnichannel retail engine.
* **REST Catalog API:**
  * Storefront Catalog: `GET https://shop.tamimimarkets.com/api/product?category={catId}&layoutType=grid`
  * Open Auth Service: OpenAPI / Swagger endpoints under `/api/v2/Auth/` (e.g. `RegisterAnonymousApp`, `TokenApp`)
  * Catalog Asset CDN: Google Cloud Storage bucket `https://storage.googleapis.com/tm-zopsmart-uploads/`
* **App Ecosystem:** White-label mobile app package `com.zopsmart.scarlet` (iOS / Android) talking directly to the ZopSmart REST API.
* **Catalog Highlights:** Premium imported groceries (Safeway Signature Select, O Organics, Kirkland), organic produce, gluten-free pantry, and fresh butchery.
* **Tax & Pricing:** Standard SAR with 15% VAT itemized; Mada, Apple Pay, Credit Cards.
* **Recommendation:** **Grade A- (7.6/10)**. Clean, structured ZopSmart REST JSON endpoints with minimal anti-bot friction, making it one of the easiest grocery platforms to query programmatically without residential proxies.

### 20. Sharaf DG Saudi Arabia (`saudi.sharafdg.com`)
* **Operator:** Sharaf Group. Premier regional consumer electronics and technology retailer.
* **Architecture:** Enterprise-tailored **WooCommerce / WordPress** frontend paired with **SAP Commerce Cloud (Hybris)** backend order management (`com.sharafdg.oms`) and Openbravo retail POS.
* **Search & Facets Engine:** **Algolia InstantSearch** powering instant query autocompletion, real-time facet filtering (`dFR[...]`), and search results.
* **Catalog & CDN:**
  * Product Categories: `https://saudi.sharafdg.com/c/{category_slug}/` (e.g. `mobiles_tablets`, `computing`, `home_appliances`, `tv_video_audio`)
  * Direct Product URLs: `https://saudi.sharafdg.com/product/{product-slug}/`
  * Image Delivery: Dedicated CDN `s.sdgcdn.com` and Cloudflare edge image optimizer (`pimcdn.sharafdg.com/cdn-cgi/image/...`)
* **Pricing & Tax:** 15% ZATCA VAT included in SAR, Apple Pay, Mada, Tabby/Tamara installments.
* **Recommendation:** **High Feasibility (7.4/10)**. Structured category taxonomy and public Algolia InstantSearch integration allow fast, automated product and price extraction.

---

## Executive Summary & Implementation Recommendations

### Top 5 Easiest Platforms to Add (Zero-Proxy / Cloudflare Worker Viable)
1. **Al-Dawaa Pharmacies (`al-dawaa.com`) \u2014 Score 8.2 / 10**: Standard SAP OCC v2 REST API (`/occ/v2/aldawaa/products/search`) returning pristine JSON with barcodes and stock.
2. **Namshi KSA (`saudi.namshi.com`) \u2014 Score 8.0 / 10**: Dedicated REST gateway (`api.namshi.com/catalog/search`) with mobile user-agent header.
3. **Alsaif Gallery (`alsaifgallery.com`) \u2014 Score 8.0 / 10**: Direct Magento 2 `POST /graphql` endpoint returning clean product schemas.
4. **Sun & Sand Sports (`en-sa.sssports.com`) \u2014 Score 7.8 / 10**: Salesforce Commerce Cloud `Search-Show` controller + client-side Algolia.
5. **Tamimi Markets (`shop.tamimimarkets.com`) \u2014 Score 7.6 / 10**: ZopSmart headless `/api/product` REST endpoints with no aggressive bot walls.

### Top Algolia Client Key Exploits (Instant Sub-50ms JSON)
* **Danube KSA (`danube.sa`)**: Exposes public Search-Only Algolia client key (`algoliasearch`), completely bypassing Spree Commerce web pages.
* **Nahdi Pharmacy (`nahdionline.com`)**: Client-side `Nahdi_Algolia` DSN endpoint queries live inventory and SFDA medications with zero Cloudflare challenge.
* **Sharaf DG KSA (`saudi.sharafdg.com`)**: Algolia InstantSearch query parameterization.

### Top GraphQL Endpoints (Single-Query Spec & Price Extraction)
* **Eddy Electronics (`eddy.com.sa/graphql`)**
* **Alsaif Gallery (`alsaifgallery.com/graphql`)**
* **Black Box KSA (`blackbox.com.sa/graphql`)**
