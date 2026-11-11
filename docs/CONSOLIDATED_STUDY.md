# Consolidated Study — State of `BAJAMIL/ideas` after the reliability & compliance work

**Date:** 2026-11-11
**Method:** full verification sweep, then 3 parallel isolated research subagents on independent domains (coverage-vs-compliance, data yield, reliability/provenance), each told to ground every claim in repo file:line evidence. The coordinating agent independently re-verified the highest-stakes claims: the "12 vs 13" count, the published reports' missing health blocks, and the fleet-score arithmetic.
**Inputs (primary sources, all in-repo):** `README.md`, `agent.py`, `marketplace_registry.py`, the 13 `*_client.py` files, `signal_health.py`, `config.py`, `tests/`, `LICENSE`, `pytest.ini`, `.github/workflows/daily-ideas.yml`, `cloudflare-worker/src/index.ts`, `DATA_EXPANSION_STUDY.md`, `CANDIDATE_MARKETPLACES_FLEET.md`, `docs/TOS_AUDIT.md`, `LATEST_IDEAS.md`, `reports/2026-11-10.md`.

---

## 0. Verification sweep (fresh, before any study)

| Check | Result | Exit |
|---|---|---|
| `python -m pytest` | **27 passed in 0.27s** | 0 |
| `python -c "import agent, config, signal_health, marketplace_registry"` | OK, `GOOGLE_NEWS_RSS_ENABLED = False` | 0 |
| `python -m compileall` (excl. tests/docs) | clean | 0 |
| `git diff --check` | clean (LF→CRLF warnings only) | 0 |
| All 8 prior deliverables present | LICENSE, TOS_AUDIT, study, plan, tests, config, pytest.ini, signal_health | — |
| HEAD / branch | `8cb1082` on `main` | — |
| Working tree | 4 modified, 3 new untracked (+ pre-existing `rtx4070_report.json`) | — |

**Bottom line: the plumbing is green.** The rest of this study is about whether the *story* built on that plumbing holds up — and it partly does not.

---

## 1. The central finding: coverage grew, identity did not

The repo now has **13 marketplace clients** (LuLu was added since the earlier audit), 9 signal collectors, and a 3-store Cloudflare Worker. Yet the three independent studies converge on one conclusion:

> **The project's stated commercial purpose — cross-store price comparison in SAR — is not achievable today.**

Evidence from the field inventory (all 13 clients read from their dataclasses / return shapes):

- **No shared product identity.** Clients emit store-local `sku`/`id`. Only Jarir carries any identifier (`isbn` for books, `item_number` from `bar_code1` metadata — `jarir_client.py:295,302`). LuLu's *source* JSON contains `ean`/`taxRate` (per `DATA_EXPANSION_STUDY.md:26`) but `lulu_client.py:85-90` **drops them**. No client emits a shared EAN/GTIN key; the Worker's inline mappings (`index.ts:154-170,191-200,227-235`) use per-store `price_sar` + `sku`, again with no shared key.
- **Inconsistent money typing.** `int` (Aqar), `float` (Jarir/eXtra/LuLu/NiceOne/GoldenScent), raw strings (Haraj/OpenSooq/Kafiil/Sabbar). Only eXtra and LuLu expose a stock field; only Jarir/eXtra are bilingual.
- **The `/api/compare` endpoint isn't a comparison.** `index.ts:67-99` juxtaposes three separate result lists under `retailers.jarir/extra/noon`; it never matches the same product across stores.

**The single missing primitive is a cross-store EAN/GTIN identity resolver** (barcode/MPN → canonical product key). This is exactly `DATA_EXPANSION_STUDY.md` Finding 5 (`:84-85`) and Tier-2 item 7 (`:111`) — still not started. A 14th scraper adds another incomparable price list, not a comparison.

### Tier-1 status (from `DATA_EXPANSION_STUDY.md:103-106`)
| Item | State | Evidence |
|---|---|---|
| LuLu free-Worker dataset | **DONE** (added since the study) | `lulu_client.py`, wired `marketplace_registry.py:33,52,217-229` |
| Signal health / provenance guard | **DONE** | `signal_health.py`, `marketplace_registry.py:20` |
| Persistence / time-series store | **NOT DONE** | Worker `Env` empty (`index.ts:12-14`); `haraj_market_engine.py` SQLite is standalone, not imported by registry |
| EAN/GTIN resolver | **NOT DONE** | no module |
| Constructor/Unbxd browse + autosuggest extensions | **NOT DONE** | Worker has only `/api/jarir`, `/api/compare`, `/api/jarir/categories`; `browse_category` just wraps `search_products` (`jarir_client.py:497`) |
| Sitemap harvest | **NOT DONE** | no sitemap code in any `.py` |

### Fleet conversion (arithmetic re-verified)
Of the 20 platforms scored in `CANDIDATE_MARKETPLACES_FLEET.md`, **exactly 1 is built** (LuLu, 6.8/10). The other 12 clients aren't among the 20 candidates; the 19 fleet names have no client.

- Built (1): sum 6.8 → avg **6.80**
- Unbuilt (19): sum **136.7** → avg **7.195**
- All 20: sum **143.5** → avg **7.175**

So the one converted platform scores **below** the unbuilt average, and the fleet doc's "Top 5 Easiest" (Al-Dawaa 8.2, Namshi 8.0, Alsaif 8.0, S&S 7.8, Tamimi 7.6 — `:223-228`) remain entirely unbuilt. *(Caveat: `DATA_EXPANSION_STUDY.md:93` downgrades Al-Dawaa to non-viable after a live 403.)* This quantifies the pattern: **past effort went to breadth, not to the identity/persistence primitives the engine needs.**

---

## 2. Coverage vs compliance: ~22 sources, zero commercial licences

Counting distinct wired sources: **9** signal collectors in `agent.py`, **13** registry clients, **4** Worker hosts → **~22 distinct** after de-duplication (VERIFIED line references; de-dup logic INFERRED). Using only the verdicts in `docs/TOS_AUDIT.md`:

| Bucket | Count | Sources |
|---|---|---|
| **HIGH** (robots-disallowed / personal-only) | **7** | Google Autocomplete, Reddit RSS, Arctic Shift, OpenSooq, Aqar, Nice One, Golden Scent |
| **Gated / already handled** | **1** | Google News RSS (`GOOGLE_NEWS_RSS_ENABLED`, default `False`) |
| **M** (unclear) | **11** | Trends, Mostaql, Khamsat, Product Hunt, Haraj, Jarir, eXtra, Etimad, Noon, LuLu, Jarir-Nuxt |
| **L / L–M** (unclear, lower friction) | **5** | HN Algolia, Salla, Syarah, Sabbar, Kafiil |

**Zero sources are declared "compliant"** (`docs/TOS_AUDIT.md` §2, §4; `README.md:77`). Only 1 of ~22 is actually gated, while §4 names ~10 more that should be default-OFF.

**If the audit's own advice were enforced:** §4's "Lowest-risk to keep" names 6 (HN Algolia, Sabbar, Syarah, Kafiil, Salla, Haraj). That leaves **~6 of 22 ≈ 27%** of the daily pipeline, and the registry would drop from 13 to 6 clients (**6/13 ≈ 46%**). Every one of those six is still `UNCLEAR`, not licensed.

### Top 5 contradictions (exact quotes + file:line, all VERIFIED)
1. `README.md:3,14` **"100% free APIs" / "100% Free Data Sources Queried Every Run"** vs audit §2: `UNCLEAR ≠ compliant`; §4: "No source is declared 'compliant'".
2. `README.md:15` **"completely bypassing Reddit's 403 rate-limiting walls"** and `agent.py:112` **"Bypasses Reddit's strict 403 API blocking"** vs `www.reddit.com/robots.txt` `User-agent: * Disallow: /` + Data API Terms §3.1/3.2 — audit §3 calls it "**Clearest breach**".
3. `README.md:31,32` and `LATEST_IDEAS.md:7,8,38,39` list **Google Autocomplete / Trends** as live free sources; audit §3 says they have "the same structural gap that got Google News disabled" and §4 recommends gating both.
4. `marketplace_registry.py:2` **"Registry (12 Platforms)"** while `:33,52` wire a **13th** (`LuluClient`). Confirmed: 13 `self.* = *Client()` instantiations, and **8 places** across `agent.py`, `marketplace_registry.py`, `signal_health.py`, `tests/test_signal_health.py` still say "12 platforms" (re-verified by grep).
5. `collect_market_intelligence()` gates **only** Google News (`agent.py:500`) yet calls Reddit/Autocomplete/Trends/HN/ProductHunt/registry unconditionally (`:487-529`); `config.py` has exactly one flag. `README.md:75` presents "disabled by default" as if the compliance problem were solved.

---

## 3. The verification story is honest about *plumbing*, not about *truth*

The reliability study re-ran every gate (all PASS) and confirmed `build_prompt()` genuinely injects `INTEGRITY_RULES` (`agent.py:45,544`) and that the health block marks failures UNAVAILABLE (`signal_health.py:44-58`). But it found a sharp gap:

- **Both published reports predate the guardrail.** `reports/2026-11-10.md` and `LATEST_IDEAS.md` (commits `20bf4ad`, 12:15) were generated before the guardrail commit (`edec0b8`, 12:27). Re-verified: all three published reports contain **0** `UNAVAILABLE` tokens and **0** `Source availability` blocks.
- **They are saturated with unsourced numeric claims** that the new `INTEGRITY_RULES` explicitly forbid:
  - `reports/2026-11-10.md:14` `"الطقس غدًا" (20,000+ daily searches)` — Google Trends RSS yields titles, autocomplete yields strings; neither yields absolute volumes.
  - `:16` `"cuaca besok" (expat influence)` — the exact behaviour `INTEGRITY_RULES:20` was written to forbid.
  - `LATEST_IDEAS.md:17` `أكثر من 63% من سكان المملكة دون سن الثلاثين` (63% under 30) — no collector returns census data.
  - `:20,91,323` `300%–600%` margins; `:84` conversion rate `>40%`; `:83` "channel #1" — no source section carries these.
  - `README.md:27` `290,000+ Saudi ministry tenders` — no fixture asserts it.
- Verdict: **every audited numeric/live claim is likely-inferred or unverifiable**, not literal-source-plausible.

### What the 27 tests do NOT cover
- **Live network behaviour** — every collector is stubbed (`tests/test_tos.py:12`, `test_agent.py:19-26`, `test_registry.py:9-13`).
- **The 13 clients' real responses** — `test_registry.py` injects a fabricated dict; no test asserts any client returns real data.
- **The LLM generation step** — `generate_with_openrouter`, `run_daily_discovery`, the Antigravity branch are untested.
- **GitHub Actions cron / deploy**, **Cloudflare Worker build**, **robots.txt enforcement**, and the `is_available()` head-only (first 200 chars) heuristic.

So **"verified" currently means "the wiring is internally consistent", not "the output is true"** — the guardrail protects *future* runs only.

---

## 4. Synthesis: what all three studies agree on

| # | Conclusion | Supported by |
|---|---|---|
| 1 | **Stop adding scrapers.** The binding constraint is identity + persistence, not coverage. | data-yield study; `DATA_EXPANSION_STUDY.md:13,85,111` |
| 2 | **The commercial promise is unfulfilled today** — `/api/compare` is a side-by-side list, not a comparison. | field inventory; `index.ts:67-99` |
| 3 | **Compliance is documented, not enforced** — ~22 sources, 0 licensed, 1 gated, ~10 more recommended for gating. | compliance study; `docs/TOS_AUDIT.md` §4 |
| 4 | **Provenance is unproven** — published reports contain unsourced numbers; the guardrail only applies to future runs. | reliability study; re-verified token counts |
| 5 | **Docs drift is measurable** — "12 platforms" in 8 places, "100% free", "bypass 403", a 13th client added without a docstring update. | all three studies; grep re-verification |

### Recommended order (derived, not started)
1. **Extract LuLu's `ean` into a canonical key** → build the EAN/GTIN resolver → then persistence/time-series. These two unlock the actual product. *(Highest value, still unstarted.)*
2. **Regenerate or annotate the published reports** with a Source availability block, or clearly label them pre-guardrail — otherwise the README describes behaviour the shipped reports don't exhibit.
3. **Fix the 8 stale "12 platforms" strings** and the README's "100% free" / "bypass 403" framing.
4. **Enforce the audit's gates** (`docs/TOS_AUDIT.md` §4) — this is a *separate bounded change* not yet implemented; note it would cut the daily pipeline to ~27%.
5. **Add live smoke tests** for at least the lowest-risk clients (HN Algolia, Sabbar, Kafiil), so "verified" starts to cover real data.

---

## 5. Limitations & boundaries

- Compliance verdicts are taken **verbatim** from `docs/TOS_AUDIT.md` (itself research, not legal advice); no new web ToS research was done in this pass. `UNCLEAR` does not mean compliant.
- The "~22 sources" and the "~27% / 46%" reductions involve de-duplication and denominator choices that are **INFERRED**; the per-source line references are VERIFIED.
- The fleet arithmetic was recomputed independently (built 6.80 / unbuilt 7.195 / all 7.175) and matches the subagent's figures up to rounding.
- The numeric-claim verdicts are based on **absence** of matching source sections plus the guardrail text — a plausible inference, not proof of fabrication (the LLM may have used general knowledge).
- This study made **no code changes, no commits, no pushes**. Working-tree changes from earlier turns remain uncommitted.
- Live endpoint behaviour (WAF blocks, 403s, current `robots.txt`) was not re-probed here; see `DATA_EXPANSION_STUDY.md:25-37` for the earlier live probes.
