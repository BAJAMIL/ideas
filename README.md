# 🇸🇦 BAJAMIL Ideas — Autonomous Saudi & Arabic Digital Product Discovery Agent

An autonomous daily research agent powered by the **Google Antigravity SDK (`google-antigravity`)** that mines **100% free APIs** every morning at **8:00 AM Saudi Time (AST)** to uncover profitable digital products, templates, Salla/Zid merchant tools, and micro-SaaS ideas for the **Saudi Arabian (KSA) & Arabic market**.

---

## 🚀 How It Works (Zero Laptop Required)

1. **GitHub Actions Cloud Scheduler** ([`.github/workflows/daily-ideas.yml`](.github/workflows/daily-ideas.yml)) wakes up daily at `05:00 UTC` (`08:00 AM Riyadh`).
2. **Google Antigravity SDK Agent** ([`agent.py`](agent.py)) loads 4 specialized skills from [`.agents/skills/`](.agents/skills/):
   - `customer-research` — Mines real Arabic & English verbatim pain points.
   - `evaluating-startup-ideas` & `idea-validation` — Scores ideas on demand, speed to build, and competition gap in KSA.
   - `offers` — Designs a complete Grand Slam Offer priced in SAR (`ر.س`).
3. **100% Free Data Sources Queried Every Run:**
   - **Reddit Free JSON API:** Mines `r/saudiarabia`, `r/SaudiProfessionals`, and `r/Riyadh` for problems, workarounds, and questions.
   - **Google Saudi Autocomplete API (`gl=sa`, `hl=ar` & `hl=en`):** Uncovers real-time search demand for Arabic Notion templates (`قالب نوشن`), Excel sheets (`نموذج إكسل`), calculators (`حاسبة`), Salla/Zid tools, and ZATCA helpers.
   - **Google Trends Saudi Arabia RSS (`geo=SA`):** Captures daily rising topics across KSA.
   - **Hacker News Algolia API & Product Hunt Feed:** Spots newly validated global digital products and micro-SaaS tools ready to be localized for Arabic RTL and Saudi buyers.
   - **Antigravity Built-in Web Search (`SEARCH_WEB` & `READ_URL_CONTENT`):** Researches Salla App Store, Zid, Mostaql, and Khamsat demand.
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
