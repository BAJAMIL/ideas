# 🇸🇦 BAJAMIL Ideas — Autonomous Saudi & Arabic Digital Product Discovery Agent

An autonomous daily research agent powered by **OpenRouter free models** (with the **Google Antigravity SDK (`google-antigravity`)** as a fallback) that mines **100% free APIs** on a daily GitHub Actions schedule to uncover profitable digital products, templates, Salla/Zid merchant tools, and micro-SaaS ideas for the **Saudi Arabian (KSA) & Arabic market**.

---

## 🚀 How It Works (Zero Laptop Required)

1. **GitHub Actions Cloud Scheduler** ([`.github/workflows/daily-ideas.yml`](.github/workflows/daily-ideas.yml)) runs the `30 1 * * *` cron daily at `01:30 UTC` (`04:30 AM Riyadh / AST`). CI first runs an import smoke test and the unit suite, then the agent.
2. **Idea Agent** ([`agent.py`](agent.py)) loads 4 specialized skills from [`.agents/skills/`](.agents/skills/):
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
   - **Etimad Saudi Government Procurement (`etimad_client.py`):** Reverse-engineered client for `tenders.etimad.sa` giving programmatic access to 290,000+ Saudi ministry tenders, RFPs, and procurement budgets.
   - **Kafiil Arabic Digital Services & Gigs (`kafiil_client.py`):** Reverse-engineered from `kafiil.com` to extract client freelance project briefs, custom software requirements, Excel automations, and digital templates.
   - **Unified Marketplace Registry (`marketplace_registry.py`):** Central multi-target orchestrator providing live health checks, uniform extraction, and latency benchmarking across all platforms.
   - **Google News Saudi Arabia RSS (`hl=ar`, `gl=SA`) — OPT-IN / DISABLED BY DEFAULT:** Tracks real-time Saudi retail news, but Google News RSS is licensed for **personal, non-commercial use only** ([Terms of Use §2](https://www.google.com/intl/en_us/terms_google_news.html)), while this agent generates commercial product ideas. Set `GOOGLE_NEWS_RSS_ENABLED=1` only for personal experimentation; see [ToS & licensing](#-tos--licensing) below.
   - **Google Saudi Autocomplete API (`gl=sa`, `hl=ar` & `hl=en`):** Uncovers real-time search demand for Arabic Notion templates (`قالب نوشن`), Excel sheets (`نموذج إكسل`), calculators (`حاسبة`), Salla/Zid tools, and ZATCA helpers.
   - **Google Trends Saudi Arabia RSS (`geo=SA`):** Captures daily rising search spikes across KSA.
   - **Hacker News Algolia API & Product Hunt Feed:** Spots newly validated global digital products and micro-SaaS tools ready to be localized for Arabic RTL and Saudi buyers.
   - **Automated Quality Filtering & Signal Tagging:** Prunes HTML noise, deduplicates near-identical titles, and automatically tags signals into `PAIN_POINT`, `UNMET_NEED`, `PAID_DEMAND`, and `MARKET_NEWS`.
4. **Daily Output:**
   - Saves a dated report in `reports/YYYY-MM-DD.md` and updates `LATEST_IDEAS.md`.
   - Opens a new **GitHub Issue** so you get a mobile/email notification with the day's top ideas.

---

## ⚙️ One-Time Setup (1 Minute)

The agent uses **OpenRouter free models** when `OPENROUTER_API_KEY` is set, and falls back to the **Google Antigravity SDK** when only `GEMINI_API_KEY` is set. At least one is required.

1. Get a free **`OPENROUTER_API_KEY`** from **[OpenRouter](https://openrouter.ai/keys)** (primary engine). Optionally also get a free **`GEMINI_API_KEY`** from **[Google AI Studio](https://aistudio.google.com/app/api-keys)** (fallback engine).
2. In this repository, go to **Settings → Secrets and variables → Actions → New repository secret** and add one or both of:
   - `OPENROUTER_API_KEY`
   - `GEMINI_API_KEY`
3. `HARAJ_SERVER_KEY` is optional — see [`.env.example`](.env.example) and [`config.py`](config.py). It overrides the public Haraj client key.
4. Go to the **[Actions tab](../../actions)**, click **Daily Saudi Digital Product Idea Discovery**, and click **Run workflow** to trigger your first report immediately!

---

## 🧪 Development & Verification

The root-level `test_*.py` files are **one-off recon/probe scripts**, not unit tests — they make live network calls and are intentionally excluded from pytest via [`pytest.ini`](pytest.ini). The real suite lives in [`tests/`](tests/).

```sh
pip install -r requirements.txt
pip install pytest
python -c "import agent"     # import smoke test (catches missing declared deps)
python -m pytest             # offline unit suite, no network calls
```

CI runs both gates before the daily agent, so a missing dependency or broken import fails the workflow instead of silently degrading to a single source.

> Note: the daily report is generated from live public signals. Sources that fail are listed as `UNAVAILABLE` in a "Source availability" block and must not be reconstructed by the model — see [`signal_health.py`](signal_health.py).

---

## ⚖️ ToS & licensing

**This project's own code is MIT licensed** — see [`LICENSE`](LICENSE). That license covers the source in this repository only; it does **not** grant any rights to the third-party data the agent queries.

**Google News RSS is disabled by default.** Its [Terms of Use §2](https://www.google.com/intl/en_us/terms_google_news.html) and the feed's own `<copyright>` element restrict it to *"personal, non-commercial use"* and forbid using it "to sell a product or service". This agent generates priced commercial product ideas, so feeding that RSS into its pipeline falls outside the license. `GOOGLE_NEWS_RSS_ENABLED` defaults to `False` in [`config.py`](config.py); when disabled, no request is made and the source is not even listed in the report's health block. Enabling it (`GOOGLE_NEWS_RSS_ENABLED=1`) is intended only for personal, non-commercial experimentation and is your responsibility.

A full **third-party source ToS / `robots.txt` audit** is in [`docs/TOS_AUDIT.md`](docs/TOS_AUDIT.md). It found concrete high-risk items — most notably Reddit's `User-agent: * Disallow: /` plus its non-commercial Public Content Policy, and robots-disallowed paths used by OpenSooq, Aqar, Nice One and Golden Scent. **No source is declared "compliant"**; several terms could not be retrieved and are recorded as UNCLEAR. Before any commercial deployment, review each source's terms and obtain the appropriate rights — this is research, not legal advice.
