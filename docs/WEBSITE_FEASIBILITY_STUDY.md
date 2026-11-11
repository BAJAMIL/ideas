# Website Feasibility Study — Arabic / Saudi AI-Content Cleanup

**Date:** 2026-11-11
**Classification:** a **spike** — a feasibility question whose output is a recommendation, not code to keep or ship. No implementation, no code changes, no commits.
**Question:** *Is it worth opening a website targeting the Arabic/Saudi "AI text cleanup" problem, using all the APIs and data we have — and what should it be called?*
**Method:** full verification sweep; 3 parallel isolated research subagents (data/API inventory, demand+feasibility, naming) with self-contained briefs; live read-only probes of the repo's **safe** public APIs; independent re-verification of quantitative claims by the coordinating agent.
**Frameworks:** `research` (primary sources, single cited Markdown file), `dispatching-parallel-agents`, `brainstorming` (spike path), `evaluating-startup-ideas`, `idea-validation`, `offers`.

---

## ⚠️ Integrity note

This document obeys the guardrail it describes (`signal_health.py:12-23` `INTEGRITY_RULES`). **No market sizes, TAMs, growth rates, conversion rates or buyer counts are stated as fact.** Every number is either (a) computed from repo files with the command shown, (b) quoted from a primary source with a URL, or (c) marked `⚠️ ESTIMATE / unverified`. Banned sales vocabulary is avoided. `UNCLEAR` ≠ compliant (`docs/TOS_AUDIT.md:8`).

**Correction to a prior answer:** last turn I quoted a "Fractl survey" (8-in-10 workers, median 45 min cleanup, 62% redid a colleague's work, 23% reached customers). Fresh verification found that attribution **unreliable** — those figures trace to *workslop* coverage, not a Fractl survey, and could not be confirmed against a primary source. **They are withdrawn and must not be used in a pitch.** `docs/CONSOLIDATED_STUDY.md:88-95` documents exactly this failure mode in the repo's own published reports.

---

## Executive summary

| Question | Answer |
|---|---|
| **Is a full website / SaaS product worth it?** | **NO.** Not on directional platform statistics, with zero buyer evidence, against a $5 commodity floor and free humanizer tools. |
| **Is a one-page site worth it?** | **YES, conditionally** — strictly as a time-boxed **validation instrument** (a fake door with a real price), not as a product. |
| **Does "we have a lot of data" help?** | **NO.** It is ~1.7 MB of legally uncleared Saudi retail listings that this product neither needs nor may lawfully use. |
| **Recommended name** | **تَنْقِيح \| Tanqih** — "source-checked revision". Tagline: *«نردّ كل رقم وادعاء إلى مصدره، ونسلّمك النص مُعلَّماً مع سجل التغييرات.»* |

The single most important finding is negative but useful: **the customer's-own-document model sidesteps the entire `docs/TOS_AUDIT.md` problem.** The audit concerns licensing of third-party data the project harvests; a text-cleanup service that only processes a document a client voluntarily sends has no source-licensing question at all.

---

## 1. What the APIs and data actually gave us

Three agents were asked to use the repo's assets. Here is what came back, with verification.

### 1.1 Local data inventory (re-verified by the coordinating agent)

Command: `python verify_counts.py` (counts files, bytes, JSON top-level list items, SQLite rows, Python lines).

| Measure | Verified value |
|---|---|
| Top-level `.json` files | **8** |
| Total JSON bytes | **1,824,995 bytes ≈ 1.74 MiB** |
| Top-level list items across those files | **834** (`haraj_100_gaming_listings` 100 + `jarir_taxonomy_tree` 12 + `stream_data` 722) |
| SQLite rows (`haraj_market.db`) | **154** (85 `listings` + 69 `price_history`) |
| Python files / lines | **102 / 8,176** |

So "a lot of data" resolves to ≈ **988 structured records** (834 + 154, *INFERRED* record definition) plus ~1.7 MB of raw harvest dumps, GraphQL introspection and category trees. Three of the four published reports are the **same file** byte-identical (`LATEST_IDEAS.md`, `docs/LATEST_IDEAS.md`, `reports/2026-11-11.md` — md5 `b16cb77b52e8`, 42,624 B). The bulk of the repo is code, recon scripts, downloaded JS/HTML bundles and AI-written prose — **not a cleaned dataset**.

### 1.2 Live read-only API probes (safe sources only)

Deliberately did **not** touch the 7 HIGH-risk sources (`docs/TOS_AUDIT.md §4`). Command: `python probe_apis.py`.

| API | Result | Reading |
|---|---|---|
| **Amazon SA autocomplete** (`DATA_EXPANSION_STUDY.md:25`, VERIFIED 200, no key) | `تدقيق نصوص` → `[]`; `محتوى ذكاء اصطناعي` → `[]`; `تصحيح محتوى` → `[]` | **Zero Arabic suggestions.** A negative demand signal from this API — but it is a *product* search, so this is weak evidence, not proof of no demand. |
| **HN Algolia** (`docs/TOS_AUDIT.md:28`, risk L) | `AI content audit` nbHits **2,789**; `AI slop cleanup` **638**; `AI humanizer` **498**; `hallucination editing` **76** | Counts of HN stories matching a query — a **weak topical-attention proxy**, NOT market demand or buyers. Do not present as demand. |
| **Salla App Store** (repo `salla_client.py`) | **19 categories**, including a first-class **`الذكاء الاصطناعي`** category. `q=تدقيق` → 4 apps (collections, SEO, ops, reporting); `q=محتوى` → 15 apps (SEO, marketing, loyalty, UGC) | **No AI-content-audit app exists in the merchant app store.** A genuine whitespace signal — but it is an *app store for merchant tools*, not a service marketplace, and "no app" ≠ "no demand". |

### 1.3 Blunt verdict on the data

`docs/TOS_AUDIT.md:8` — **zero sources declared "compliant"**; §4:57 "Do not label any source 'compliant'"; `README.md:77` says so. The MIT `LICENSE` covers repo code only (`docs/TOS_AUDIT.md:69`), granting no third-party data rights. A website built on this scraped data would inherit those rights problems wholesale; `docs/BUSINESS_IDEAS.md:141` already lists "launch the ~22-source commercial data product" as an **anti-idea**.

Technically it is also the wrong data: there is no corpus of Arabic work documents, no AI-tell labels, no tone annotations, no customer records, no Arabic NLP (`requirements.txt` = `google-antigravity`, `httpx`, `python-dotenv`, `beautifulsoup4`; no `camel-tools` / `farasa` / `hazm` / `transformers`). The only transferable asset is the **method**: `signal_health.py:12-23` `INTEGRITY_RULES` (forbid invented numbers/terms, require "insufficient data", literal citation) — pure text, network-free, MIT-licensed, zero third-party data. That is a discipline, not a dataset.

---

## 2. Demand and competition (fresh verification)

| Claim | Source | Verdict |
|---|---|---|
| Freelancer.com "correct AI / hallucination / error" listings **+87% → 10,760** (Aug 2025–Jun 2026); Upwork remediation gigs **+70% YoY**; Fiverr "AI cleanup" searches **>20×** since 2023 | [Guardian](https://www.theguardian.com/technology/2026/sep/02/ai-jobs-freelance-cleanup), [Search Engine Journal](https://www.searchenginejournal.com/ai-slop-cleanup-job-listings-report/588235/) | **VERIFIED AS REPORTED / DIRECTIONAL** — platform-internal data, explicitly unaudited; the three platforms measure different things and cannot be summed |
| Four **PwC Middle East** reports with fake footnotes, incl. a hallucinated paper on *air quality in Riyadh* (Jul 2026) | [FT](https://www.ft.com/content/7e149ac8-2ce2-4266-8940-192f9821b33c), [GPTZero](https://gptzero.me/news/investigations-pwc) | **VERIFIED** — the strongest KSA-specific proof point for a sales conversation |
| Arabic ≈ **0.5% of web content** (Qatar's Fanar researchers); Saudi/Gulf dialect + register failures; "unlived Arabic" | [Fast Company ME](https://fastcompanyme.com/technology/what-does-an-ai-watermark-mean-for-arabic-culture/) | **VERIFIED** — the technical moat is real |
| "A fast draft is not publish-ready content"; tone before grammar; **PDPL** warning on pasting customer data into public AI tools | [Origami.sa](https://origami.sa/en/blog/generative-ai-arabic-marketing-content/) (Saudi agency, 11 Jun 2026) | **VERIFIED** |
| Ipsos/ABG UAE+KSA: **70% concerned** about overreliance without human oversight | [Ipsos](https://www.ipsos.com/en-ae/pilots-performance-building-mature-ai-ecosystem-agencies-and-advertisers) | **VERIFIED (70%)**; but "112 professionals / 68% / 2026" is **UNVERIFIED** — the page says "100+", 96% used AI tools, dated 30.06.**2025**. ⚠️ Survey, not buyer counts |
| Deloitte "Arab Media in the Age of AI": provenance + human-in-the-loop | [Deloitte](https://www.deloitte.com/middle-east/en/Industries/tmt/perspectives/arab-media-in-the-age-of-ai.html) | **PARTIAL / UNVERIFIED** — the quoted "provenance" wording and "KSA 70%" are not on the public page. Forecast, not buyer counts |
| **The exact service is already sold in Arabic** | [Khamsat](https://khamsat.com/writing/proofreading/4010103-التدقيق-والتصحيح-العلمي-لمحتويات-ونصوص-الذكاء-الاصطناعي) ($5 / 400–500 words), [Kafiil](https://kafiil.com/service/227684-المراجعة-والتدقيق-اللغوي-والأخلاقي-للنصوص-والمحتوى) ($5), [Mostaql](https://mostaql.com/project/1249330-محرر-ومدقق-لمحتوى-بحث) (buyer wrote "عدم استخدام الذكاء الاصطناعي", $25–50) | **VERIFIED** — real demand, but at commodity prices |
| **NEW:** Khamsat now lists "**تدقيق محتوى AI**" as a category; a buyer request asks for "مراجعة بشرية… أنسنة المحتوى" | `khamsat.com` | **VERIFIED** — the category exists, i.e. demand is organized, not a lone gig |
| **NEW:** Arabic AI humanizer/detector SaaS already exists (`aidetector.pro`, `humanifyer.com`, `gptcleanup.com`, Undetectable.ai) | as listed | **VERIFIED** — crowded, and several sell detector *bypass* |
| Arabic AI-tell word lists are weakly sourced | `content-locale-humanize-ar` skill ("sourcing confidence: the weakest of any language checked") | **VERIFIED** — do not build an automated "AI tell detector" |
| Disclosure pressure: SDAIA guidance, Google Ads AI-labelling (Jul 2026), Meta/TikTok | [Google Ads policy](https://support.google.com/adspolicy/answer/17257106), [Eclipse Agency](https://www.eclipseagency.net/blog/ai-marketing-saudi-arabia) | **VERIFIED** — sell auditing, never hiding |

**Counter-signal (same Guardian piece):** freelancers expect humanizing work to "dry up within five to 10 years as models improve". Demand is real but possibly transient. And the Guardian reports clients **lowball** cleanup work.

---

## 3. Verdict on the website

### (a) Full product / SaaS site — **NO**

Conditions to reconsider *only*: ≥1 paid invoice from a cold stranger (`docs/BUSINESS_IDEAS.md:155,177`), written data-rights clearance, and a defensible price above the ~$5 commodity floor.

Reasons:
1. `docs/CONSOLIDATED_STUDY.md:27` — 13 clients and a 20-platform research fleet were built **before any buyer conversation**; `docs/TOS_AUDIT.md:6` — no revenue. A full site repeats that exact mistake.
2. Demand stats are platform-internal and directional, not buyer counts.
3. The service is already commoditized (Khamsat category, $5 gigs, free humanizer SaaS).
4. The only real moat — native Saudi/Gulf register — requires a **human editor**, which is a service, not scalable software (`content-locale-humanize-ar` confirms Arabic tell-lists are unreliable).
5. `docs/BUSINESS_IDEAS.md:29`: the most important conclusion is negative — don't launch on unverified numbers.

### (b) One-page fake door / lead-gen site — **YES, conditionally**

Endorsed by the repo itself: `docs/BUSINESS_IDEAS.md:66` ("one paid 48-hour fake door"), `:159` ("fake door with a real price, zero scrapers"), `:179` (Step 4). Per `idea-validation`, validate demand **before** code; the site is a **measuring device, not a product**.

Conditions: a real stated SAR price; no accounts, no upload storage, no AI processing, no scrapers; the CTA must ask for **money** (paid pilot deposit / pre-product invoice), not an email; pre-declared pass/fail and a time box. **A page with no traffic is a null experiment** — pair it with 20 cold outbound contacts (`docs/BUSINESS_IDEAS.md:176`).

### Riskiest assumption and cheapest falsification

**Assumption:** a KSA/GCC buyer will pay a foreign, no-local-entity provider a premium to clean up their *own* Arabic work documents, repeatedly, instead of a $5 Khamsat/Kafiil gig, a free humanizer, their own LLM, or an in-house editor. This bundles willingness-to-pay, cross-border trust and preference over cheaper substitutes — the repo's #1 ranked assumption (`docs/BUSINESS_IDEAS.md:155`).

**Cheapest experiment:** 48-hour one-page fake door at a real price + 20 cold outbound contacts + a pre-product invoice/deposit ask for **one hand-edited Wizard-of-Oz document**. **Pass** = ≥1 paid deposit from a stranger. **Fail** = polite interest, email signups or silence → stop. No code, no accounts, no backend.

### Business math — ⚠️ all ESTIMATE

`⚠️ ESTIMATE / unverified`: `⚠️` SAR 300 per document audit × `⚠️` 2 documents/month × `⚠️` 12 months = `⚠️` SAR 7,200 ACV × `⚠️` 20 retained clients = `⚠️` SAR 144,000/yr. **Every input is invented; this is arithmetic, not a forecast.** The repo has zero buyer evidence (`docs/TOS_AUDIT.md:6`). The `⚠️` SAR 300 price is the weakest input, given $5 competitors.

---

## 4. Compliance / decision rule for the website

**May touch:** only the customer's own document, voluntarily supplied with explicit consent, processed transiently, then deleted.

**May not touch:** any scraped third-party data — marketplace listings, Reddit / Google Trends / Autocomplete, retailer catalogs, any of the ~22 sources in `docs/TOS_AUDIT.md`.

**A customer-owned-document model avoids the audit problem entirely.** `docs/TOS_AUDIT.md` concerns licensing of data the project *harvests from third parties*; with no third-party ingestion, the HIGH / UNCLEAR verdicts are irrelevant. This is the same logic as "Claim Ledger": pure text processing of the customer's own draft (`docs/BUSINESS_IDEAS.md:43,129`).

**PDPL:** if a document holds personal data, Saudi PDPL (SDAIA) applies; Origami.sa warns pasting customer data into public AI tools may violate it. The operator is outside KSA, so cross-border processing is an open question — **confirm with counsel**, not asserted here (`docs/TOS_AUDIT.md:8` is research, not legal advice). **Disclosure:** SDAIA guidance and platform labelling rules push toward disclosure; the service must support it, never evade it.

---

## 5. Day-one scope (YAGNI) and prohibited claims

**Does:** one static page with (1) one specific service — "human review of Arabic work documents: invented facts/numbers, wrong Saudi/Gulf register, AI tells"; (2) one real SAR price, one deliverable (annotated doc + change log), one CTA "request a paid pilot"; (3) a plain privacy/disclosure note (what data, where processed, retention/deletion, no third-party AI tools on your data, "we do not help hide AI use"); (4) email/WhatsApp contact. **No** accounts, login, stored uploads, payment gateway, dashboard, API, detector, scraper or AI processing. Invoice manually.

**Must NOT claim:** "AI detector", "% AI-written" or any AI score (Arabic detection unreliable); "bypass / undetectable" or any evasion of AI-use disclosure; "100% guaranteed" (use the paid-pilot conditional exit, `docs/BUSINESS_IDEAS.md:96`); any market size / growth / conversion figure as fact; any KSA presence, local entity or local address; any banned sales vocabulary.

---

## 6. Name: تَنْقِيح | Tanqih

**Recommended.** Arabic **تنقيح** = critical revision / refinement of a text (تنقيح النصوص = textual verification). It names the **method**, not the machine; it is one short word, spells unambiguously in Latin, and an obvious-brand screen surfaced no clear collision (⚠️ UNVERIFIED, not trademark clearance).

- **Arabic tagline:** «نردّ كل رقم وادعاء إلى مصدره، ونسلّمك النص مُعلَّماً مع سجل التغييرات.»
- **English tagline:** "Every figure and claim traced to its source — delivered as a marked-up redline and a change log."

**Runner-up سَنَد / Sanad** ("documentary evidence") is semantically perfect but the screen found 6+ active Saudi/Gulf "Sanad" brands, two finance entities, Jordan's `sanad.gov.jo` government digital-ID platform and Al Jazeera's Sanad fact-check unit — a trademark risk and a direct hit on the "don't be confused with a government body" constraint.

**Rejected:** ميزان / Mizan (suspected Meezan Bank + Quranic authority overtones), رصد / Rasd (surveillance/detection register → drifts toward AI-detector framing), تدقيق / Tadqiq (the generic category word buyers already use — cannot be a named offer).

**English alternates** (use only on the foreign-entity surface): *Sourcebound* (international landing page / email domain), *Redline Audit* (named offer on proposals/invoices), *Claim Ledger* (deliverable title). Saudi-facing copy and Khamsat/Kafiil/Mostaql gig titles stay تنقيح.

**Positioning caveat:** copy saying «إزالة آثار الذكاء الاصطناعي / إخفاء / تجاوز الكشف / نسبة التوليد» attracts buyers seeking detector evasion. Put the boundary in the FAQ **and** onboarding: «لا نتحقق من نسبة التوليد ولا نساعد على إخفاء استخدام الذكاء الاصطناعي؛ نُدقّق الأرقام والادعاءات ونُوثّق كل تعديل وسببه.» Sell the audit, the redline and the log — never the disappearance.

**Pre-commit checklist (all UNVERIFIED — none run):** (1) domains `tanqih` across .com/.sa/.com.sa/.co + misspellings + Arabic IDN; (2) SAIP trademark search (Nice 35/41/42) **and** Ministry of Commerce trade-name reservation — these are different; (3) authority collision with SDAIA / ZATCA / MCIT / .gov.sa; (4) seller names, gig titles and slugs on Khamsat, Kafiil, Mostaql, Ureed; (5) handles on X (primary Saudi B2B channel), LinkedIn, Instagram; (6) 2–3 native-Saudi readers say the name + tagline aloud and answer unprompted "what does this do?" — check for Egyptian/Levantine read, stiff literary MSA, religious/legal authority, or "AI detector" read.

---

## 7. Validation-first sequence (no code until a stranger pays)

| Step | Artefact | Pass / fail |
|---|---|---|
| 1 | **20 cold-customer interview notes** — what do you already pay to fix in Arabic work documents? | Pass = repeated, specific, already-paid-for workflow. Fail = polite interest → STOP |
| 2 | **One-page fake door** named تنقيح, real SAR price, "request a paid pilot" CTA | Pass = ≥1 paid deposit from a cold stranger. Fail = email signups / silence → STOP |
| 3 | **One hand-edited Wizard-of-Oz audit** of a real client document — redline + change log, every number traced | Pass = buyer asks for week 2 AND all figures trace to source. Fail = untraceable claims → STOP |
| 4 | **Written rights + disclosure pack** for exactly the data Step 3 used | Pass = written consent + no third-party ingestion. **Only now write code** |

---

## 8. Limitations & boundaries

- **Compliance verdicts are inherited** from `docs/TOS_AUDIT.md` (research, not legal advice). No new ToS review here.
- **Demand figures are platform-internal, directional and unaudited**; the withdrawn "Fractl" figures must not be reused. HN Algolia `nbHits` and Amazon autocomplete results are weak topical proxies, **not** demand data.
- **All business math is `⚠️ ESTIMATE`.** Zero customers, invoices, ACV or conversion evidence exists in the repo (`docs/TOS_AUDIT.md:6`).
- **"No AI-content-audit app in Salla App Store" is a whitespace signal, not proof of demand** — an app store for merchant tools ≠ a service marketplace.
- **The name is not cleared.** Domain, SAIP/MoC, board, handle and native-Saudi register checks are all UNVERIFIED and are the user's to run.
- **Arabic fluency is the deciding fork.** The core deliverable requires native/near-native Arabic with Saudi register sensitivity (`Alignerr` Arabic-language-expert role, $40–120/hr remote, requires exactly that). If the operator lacks it, the model becomes an agency with a subcontracted editor — a different, harder business with thinner margin. This study does not assume that question is answered.
- **Why-now is weak:** the red-team study found no dated, primary-source-verified external inflection in the repo; several candidates are headwinds (PA-API 5 dead, X free tier ended Feb 2026).
- **This is a spike / recommendation.** No code, tests, files outside `docs/WEBSITE_FEASIBILITY_STUDY.md`, commits or pushes. Live API probes were read-only, on safe sources only, and touched none of the 7 HIGH-risk sources.
