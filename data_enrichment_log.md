# Data Enrichment Log

This log documents every addition and correction made to the starter dataset for the Ethiopia Financial Inclusion Forecasting challenge, per Task 1's requirements. All work here is by **Maedot Amha**, collected **2026-07-21**, unless attributed to the original starter export (`Example_Trainee`, `2025-01-20`).

## 1. What we started with

The starter file was provided as a two-sheet Excel workbook:
- **Sheet 1 ("data")** — observations, targets, and events. This sheet exported and was fully recovered: **43 records** (30 observations, 3 targets, 10 events).
- **Sheet 2 ("impact_links")** — modeled event -> indicator relationships. **This sheet did not export** and none of its 14 rows were recoverable from the files we received.

We also received a supplementary "Additional Data Points Guide," of which only Sheet A (Alternative Baseline Surveys) exported; Sheets B (Direct Correlates), C (Indirect Correlates/Enablers), and D (Market Nuances) were not recoverable as files, though their content is summarized in the challenge brief itself and we used that summary directly (e.g., Market Nuance D — P2P dominance, thin agent activity, low mobile-money-only usage, easy bank account access, low credit penetration — is referenced explicitly in the notes of several records below).

## 2. Reconstructing the impact_links sheet (25 records: IMP_0001–IMP_0025)

Since the original impact_link data was unrecoverable, we built it from scratch following the schema rules in `SCHEMA.md` (pillar assigned to the *affected indicator*, never pre-assigned to the event) and Task 3's explicit instruction to use comparable-country evidence where Ethiopian pre/post data is insufficient.

Methodology:
- For each of the 10 starter events (and 3 new events we added — see §4), we identified plausible affected indicators based on (a) direct empirical before/after Ethiopian data where available (e.g., Telebirr -> mobile money account rate), (b) documented effects from comparable markets (Kenya M-Pesa via Suri & Jack 2016; Tanzania mobile money interoperability; India Aadhaar/UPI), or (c) domain-expert judgment where neither was available.
- Every impact_link's `evidence_basis` field is set honestly to `empirical`, `literature`, `theoretical`, or `expert` — we did **not** mark judgment calls as empirical.
- `impact_magnitude` follows the reference_codes definitions (high >15%, medium 5–15%, low <5%, negligible <1%).
- Full reasoning and validation-against-actuals is in `notebooks/03_impact_modeling.ipynb`.

This is the single largest piece of enrichment work and should be read as **our modeled interpretation**, not verified source data — treat every impact_link's magnitude/direction as a hypothesis to sanity-check, not a fact.

## 3. New observations added (REC_0034–REC_0044)

| ID | Indicator | Value | Why it matters |
|---|---|---|---|
| REC_0034 | `USG_DIGITAL_PAYMENT` (Digital Payment Adoption Rate) | 35% (2024) | **Critical gap fix.** This is one of the two forecasting targets required by the challenge (Usage pillar) and was completely absent from the starter export. Sourced from the Global Findex 2024 round (published in the 2025 Database release), matching the figure cited in the challenge brief itself. |
| REC_0035 | `USG_WAGE_DIGITAL` (Digital Wage Receipt Rate) | 15% (2024) | Depth-of-usage indicator cited in the challenge brief; useful context for the Usage pillar. |
| REC_0036 / REC_0037 | `ACC_OWNERSHIP` by gender (male 57%, female 42%) | 2024 | The starter data only had a 2021 gender split (REC_0004/REC_0005); the 2024 split is essential for tracking whether the gender gap widened or narrowed. |
| REC_0038 | `ACC_OWNERSHIP`, urban | 73% (2024) | No sourced rural-specific 2024 figure was found — we deliberately did **not** fabricate one via residual calculation, since we couldn't verify a reliable urban population weight. The 49% national vs. 73% urban comparison is still directly usable as an inclusion-gap signal. |
| REC_0039 | `GEN_GAP_ACC` (refined) | 15pp (2024) | The starter REC_0028 recorded an *estimated*, medium-confidence 18pp gap. The officially published Findex 2025 release gives 15pp (57% vs 42%). We kept REC_0028 for transparency and added REC_0039 as the higher-confidence figure — see §5 for the discrepancy note. |
| REC_0040 | `ACC_ATM_DENSITY` | 10.07 per 100k adults (2023) | IMF Financial Access Survey — supply-side infrastructure indicator (Enrichment Guide Sheet B: "Direct Correlation"). |
| REC_0041 | `ACC_BRANCH_DENSITY` | 14.26 per 100k adults (2023) | IMF FAS — supports the Market Nuance that bank branch access is not Ethiopia's binding constraint. |
| REC_0042 | `ACC_MM_AGENTS` | 415,000 agents (2024) | NBE-derived agent network size, up from ~200,000 in Sept 2022. |
| REC_0043 | `USG_AGENT_ACTIVITY_RATE` | 20% weekly-active (2025) | Low-confidence, single trade-press source, but directly supports the "registered vs. active" gap analysis called for in Task 2 — most mobile money agents barely transact. |
| REC_0044 | `ACC_FAYDA` | 29.5M enrolled (Jan 2026) | Extends the Fayda enrollment series past the starter data's May-2025 (15M) point, ahead of the 90M-by-2028 target. |

## 4. New events added (EVT_0011–EVT_0013)

| ID | Category | Event | Why it matters |
|---|---|---|---|
| EVT_0011 | `partnership` | Safaricom-Government Fayda enrollment partnership (7 regions) | A second enrollment channel plausibly accelerates Fayda uptake beyond Ethio Telecom alone. Date is approximate — flagged `confidence: medium`. |
| EVT_0012 | `regulation` | Fayda mandated for all banking transactions (by 2026) | A strong forcing function for digital ID + account KYC; genuinely ambiguous net effect on Access (formalizes accounts, but risks temporarily excluding the unenrolled) — modeled with `impact_direction: mixed` in IMP_0023. |
| EVT_0013 | `milestone` | Fayda enrollment surpasses 29.5M | Signals rollout acceleration ahead of the EVT_0012 mandate. |

All three are sourced from news/industry-press coverage (Biometric Update, ID Tech Wire) rather than primary regulator publications, hence `confidence: medium` throughout, and dates are explicitly flagged as approximate where the source snippet didn't pin down an exact day.

## 5. Data quality notes and discrepancies

- **Gender gap discrepancy:** starter data (REC_0028, medium confidence) estimated an 18pp 2024 gender gap; the officially published Findex 2025 figure is 15pp (REC_0039, high confidence). Both are retained — see Task 2's data quality assessment for how this is handled in analysis.
- **Digital payment adoption ambiguity:** some 2024/2025 Findex press coverage cites much lower shares for specific payment sub-behaviors (6% in-store, 7% online bill pay, 1% online purchase) than the 35% "made or received a digital payment" composite figure used in REC_0034. These are not contradictory — they measure narrower activities — but the gap is wide enough that we flag it as a genuine data-quality caveat rather than reconciling it silently.
- **No fabricated rural figure:** we chose not to back-calculate a rural account-ownership number from the national/urban split, since we lacked a sourced, current urban population-share weight to do so credibly. This is a real gap in our disaggregated coverage.
- **Approximate event dates:** EVT_0011 and EVT_0012 dates are best estimates from press coverage, not confirmed regulatory effective dates — treat any lag-month calculations involving them as lower-confidence.

## 6. Net result

| record_type | Starter | After enrichment |
|---|---|---|
| observation | 30 | 41 |
| target | 3 | 3 |
| event | 10 | 13 |
| impact_link | 0 (unrecoverable) | 25 |
| **Total** | **43** | **82** |
