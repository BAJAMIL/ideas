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
| 2 | **Amazon SA** | General Retail & Tech | Custom Amazon A9 / HTML | High (WAF / Captcha) | Partial (Needs headers) | *Evaluating...* | Running |
| 3 | **Lulu Hypermarket** | Grocery & Department Store | SAP Hybris / Algolia | Moderate | Yes | *Evaluating...* | Running |
| 4 | **Panda / Panda Click** | Hypermarket & Groceries | Custom App / Cloudflare | Moderate | Yes | *Evaluating...* | Running |
| 5 | **Danube / BinDawood** | Premium Grocery & Imports | Algolia / Magento | Moderate | Yes | *Evaluating...* | Running |
| 6 | **Carrefour KSA** | Hypermarket & Electronics | Carrefour Global API / Algolia | Moderate | Yes | *Evaluating...* | Running |
| 7 | **Tamimi Markets** | Specialty Groceries | Custom E-Comm Engine | Low / Moderate | Yes | *Evaluating...* | Running |
| 8 | **Virgin Megastore** | Gaming, Tech & Culture | Magento / Algolia / Klevu | Moderate | Yes | *Evaluating...* | Running |
| 9 | **Sharaf DG KSA** | Electronics & Appliances | Enterprise Search Engine | Moderate | Yes | *Evaluating...* | Running |
| 10 | **Black Box KSA** | Consumer Electronics & TV | Magento / Custom | Low / Moderate | Yes | *Evaluating...* | Running |
| 11 | **Eddy Electronics** | Furniture & Appliances | Magento / Custom | Low / Moderate | Yes | *Evaluating...* | Running |
| 12 | **Alsaif Gallery** | Kitchenware & Small Appliances | Salla / Custom Magento | Low / Moderate | Yes | *Evaluating...* | Running |
| 13 | **Nahdi Pharmacy** | Healthcare & Baby Care | Oracle Commerce / Algolia | Moderate | Yes | *Evaluating...* | Running |
| 14 | **Al-Dawaa Pharmacies**| Health & Beauty Care | Magento / Custom API | Moderate | Yes | *Evaluating...* | Running |
| 15 | **Namshi KSA** | Fashion & Footwear | Custom Microservices / Algolia | Moderate | Yes | *Evaluating...* | Running |
| 16 | **Sivvi KSA** | Fashion (Noon Ecosystem) | Noon Catalog API / Algolia | Moderate | Yes | *Evaluating...* | Running |
| 17 | **Ounass KSA** | Luxury Designer Apparel | Algolia / Bloomreach | Moderate | Yes | *Evaluating...* | Running |
| 18 | **Sun & Sand Sports** | Sports & Athletic Apparel | Salesforce Commerce Cloud | Moderate / High | Partial | *Evaluating...* | Running |
| 19 | **Zid Ecosystem** | Saudi Merchant Stores | Zid Multi-Tenant API (`api.zid.sa/v1/`) | Moderate (OAuth2 / Dual Token) | Yes (Partner/Merchant) | **7.7 / 10** | **Evaluated** |
| 20 | **Boutiqaat KSA** | Beauty, Perfume & Influencers | Custom Microservices | Moderate | Yes | *Evaluating...* | Running |

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

