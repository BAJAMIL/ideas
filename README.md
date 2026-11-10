# 🇸🇦 BAJAMIL Ideas — Autonomous Saudi & Arabic Digital Product Discovery Agent

An autonomous daily research agent powered by the **Google Antigravity SDK (`google-antigravity`)** that mines **100% free APIs** every morning at **8:00 AM Saudi Time (AST)** to uncover profitable digital products, templates, Salla/Zid merchant tools, and micro-SaaS ideas for the **Saudi Arabian (KSA) & Arabic market**.

---

## 🚀 How It Works (Zero Laptop Required)

1. **GitHub Actions Cloud Scheduler** ([`.github/workflows/daily-ideas.yml`](.github/workflows/daily-ideas.yml)) wakes up daily at `05:00 UTC` (`08:00 AM Riyadh`).
2. **Google Antigravity SDK Agent** ([`agent.py`](agent.py)) loads 4 specialized skills from [`.agents/skills/`](.agents/skills/):
   - `customer-research` — Mines real Arabic & English verbatim pain points.
   - `evaluating-startup-ideas` & `idea-validation` — Scores ideas on demand, speed to build, and competition gap in KSA.
   - `offers` — Designs a complete Grand Slam Offer priced in SAR (`ر.س`).
3. **100% Free Data Sources Queried Every Run (Zero Paid APIs):**
   - **Multi-Tier Saudi Reddit Engine:** Mines `r/saudiarabia`, `r/SaudiProfessionals`, and `r/Riyadh` via Atom/RSS query feeds and Arctic Shift fallback, completely bypassing Reddit's 403 rate-limiting walls.
   - **Mostaql Verified Paid Projects:** Scrapes active freelance and business project requests directly from Mostaql to see what Saudi & Arab clients are actively paying for right now.
   - **Khamsat Unmet Service Requests:** Mines the "طلبات الخدمات غير الموجودة" community board to discover unbuilt software, automations, and digital tools buyers are pleading for.
   - **Jarir Bookstore Discovery Engine (`jarir_client.py`):** Reverse-engineered from Jarir Bookstore KSA (`jarir.com/sa-en/`) via live Constructor.io discovery APIs (`key_KcSYfmQTEwRpBnd9` English / `key_g0Gi7pKaE5cyqDGl` Arabic), extracting real-time laptop, tech, gaming, book, and accessories pricing, SKU metadata, GTM discounts, and search autocomplete suggestions.
   - **eXtra Stores Retail & Clearance Deals (`extra_client.py`):** Reverse-engineered from United Electronics / eXtra KSA (`extra.com`) via Unbxd Discovery APIs across dual Arabic & English indexes, tracking live electronics pricing, wasPrice discount percentages, brand matching, and clearance margins.
   - **Noon Saudi Arabia Catalog Search (`noon_client.py`):** Reverse-engineered from Noon KSA (`noon.com`) catalog v3 microservice, tracking consumer product ratings, reviews, Noon Express fulfillment status, and real-time market prices in SAR.
   - **Haraj Marketplace Demands (`haraj_client.py` & `haraj_market_engine.py`):** Reverse-engineered from Saudi Arabia's largest marketplace (`haraj.com.sa`) via Apollo GraphQL and SSR streams, with an integrated SQLite price history database and arbitrage anomaly detector.
   - **OpenSooq Saudi Arabia (`opensooq_client.py`):** High-throughput reverse-engineered client extracting typed listings, pricing, sub-neighborhoods, seller verification levels, and WhatsApp contact indicators from Next.js SSR state.
   - **Salla Merchant App Store (`salla_client.py`):** Reverse-engineered from Salla's Developer Marketplace API (`api.salla.dev/marketplace/v2`) across 19 categories (AI, WhatsApp bots, marketing, ERP, ZATCA accounting) to identify proven revenue-generating micro-SaaS pricing (SAR/mo) and merchant demand.
   - **Aqar Real Estate Engine (`aqar_client.py`):** Reverse-engineered from Next.js streaming RSC payloads (`sa.aqar.fm`) to capture verified property listings with official REGA prices, RNPL installment rates, exact GPS coordinates, and district IDs.
   - **Syarah Certified Automotive (`syarah_client.py`):** Reverse-engineered automotive client extracting certified dealer and private vehicles with cash vs. monthly installment pricing, 200-point inspection status, and technical odometer/engine specs.
   - **Sabbar Hourly & Operational Jobs (`sabbar_client.py`):** Reverse-engineered from structured job schemas (`sabbar.com`) tracking live corporate hiring, operational salaries, and workforce demands.
   - **Unified Marketplace Registry (`marketplace_registry.py`):** Central multi-target orchestrator providing live health checks, uniform extraction, and latency benchmarking across all platforms.
   - **Google News Saudi Arabia RSS (`hl=ar`, `gl=SA`):** Tracks real-time Saudi retail, e-commerce, startup, and fintech news developments.
   - **Google Saudi Autocomplete API (`gl=sa`, `hl=ar` & `hl=en`):** Uncovers real-time search demand for Arabic Notion templates (`قالب نوشن`), Excel sheets (`نموذج إكسل`), calculators (`حاسبة`), Salla/Zid tools, and ZATCA helpers.
   - **Google Trends Saudi Arabia RSS (`geo=SA`):** Captures daily rising search spikes across KSA.
   - **Hacker News Algolia API & Product Hunt Feed:** Spots newly validated global digital products and micro-SaaS tools ready to be localized for Arabic RTL and Saudi buyers.
   - **Automated Quality Filtering & Signal Tagging:** Prunes HTML noise, deduplicates near-identical titles, and automatically tags signals into `PAIN_POINT`, `UNMET_NEED`, `PAID_DEMAND`, and `MARKET_NEWS`.
4. **Daily Output:**
   - Saves a dated report in `reports/YYYY-MM-DD.md` and updates `LATEST_IDEAS.md`.
   - Opens a new **GitHub Issue** so you get a mobile/email notification with the day's top ideas.

---

## ⚙️ One-Time Setup (1 Minute)

1. Get a free `GEMINI_API_KEY` from **[Google AI Studio](https://aistudio.google.com/app/api-keys)**.
2. In this repository, go to **Settings → Secrets and variables → Actions → New repository secret**.
3. Add:
   - **Name:** `GEMINI_API_KEY`
   - **Secret:** *(your Google AI Studio key)*
4. Go to the **[Actions tab](../../actions)**, click **Daily Saudi Digital Product Idea Discovery**, and click **Run workflow** to trigger your first report immediately!
