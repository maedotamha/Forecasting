# Ethiopia Financial Inclusion — Unified Data Format v2

## Key Design Principle

**Don't force interpretation onto data.**

An earlier version of this schema assigned events to pillars directly (e.g., "Telebirr Launch" -> USAGE). That is **biased**, because:
- Telebirr affects both ACCESS and USAGE
- Fayda affects ACCESS, GENDER, and TRUST
- Pillar assignment is an **interpretation**, not a fact

## The Correct Approach

| Record Type | `category` column | `pillar` column |
|---|---|---|
| `observation` | (empty) | **YES** — what dimension is measured |
| `target` | (empty) | **YES** — what dimension is the goal |
| `event` | **Event type** (policy, product_launch, etc.) | **(empty)** — no pre-assignment |
| `impact_link` | (empty) | **YES** — pillar of the affected indicator |

---

## How It Works

### Events are neutral
```csv
EVT_0001,,event,product_launch,,Telebirr Launch,...
```
- `category` = what type of event (`product_launch`)
- `pillar` = empty (no pre-interpretation)

### Impact links capture effects
```csv
IMP_0001,EVT_0001,impact_link,,ACCESS,...,ACC_MM_ACCOUNT,direct,increase,high,4.7,6,...
```
- One event -> multiple impact_links
- Each impact_link has a `pillar` (derived from the affected indicator, not the event)
- `parent_id` links the impact_link back to its event via `record_id`

### Query: "What affects ACCESS?"
```python
access_impacts = df[(df.record_type == "impact_link") & (df.pillar == "ACCESS")]
access_events = access_impacts.merge(
    df[df.record_type == "event"],
    left_on="parent_id", right_on="record_id", suffixes=("", "_event"),
)
```

---

## Event Categories

| category | Description | Examples |
|---|---|---|
| `product_launch` | New product/service | Telebirr, M-Pesa |
| `market_entry` | New competitor | Safaricom Ethiopia |
| `market_exit` | Competitor leaves | — |
| `policy` | Government strategy | NFIS-II |
| `regulation` | Regulatory directive | Fayda banking mandate |
| `infrastructure` | System deployment | Fayda, EthioPay |
| `partnership` | Integration | M-Pesa + EthSwitch |
| `milestone` | Achievement | P2P > ATM |
| `economic` | Macro shock | FX reform |
| `pricing` | Price change | Safaricom rate hike |

## Pillar Definitions (for observations/targets/impact_links)

| pillar | Measures |
|---|---|
| `ACCESS` | Can people reach services? |
| `USAGE` | Are people using services? |
| `AFFORDABILITY` | Can people afford services? |
| `GENDER` | Gender gaps |
| `QUALITY` | Do services work reliably? |
| `TRUST` | Do people trust the system? |
| `DEPTH` | Beyond payments (savings, credit)? |

---

## Data Entry Rules

**Adding an observation**
```
record_type: observation
category: (leave empty)
pillar: ACCESS | USAGE | GENDER | ...
indicator_code: ACC_OWNERSHIP, USG_DIGITAL_PAYMENT, etc.
```

**Adding an event**
```
record_type: event
category: product_launch | policy | infrastructure | ...
pillar: (leave empty — don't pre-assign!)
indicator: Event name
```

**Adding an impact link**
```
record_type: impact_link
parent_id: The event ID (EVT_XXXX)
category: (leave empty)
pillar: The pillar of the affected indicator
related_indicator: The indicator code being affected
```

---

## Column Reference (this project's CSV)

`record_id, parent_id, record_type, category, pillar, indicator, indicator_code, indicator_direction, value_numeric, value_text, value_type, unit, observation_date, period_start, period_end, fiscal_year, gender, location, region, source_name, source_type, source_url, confidence, related_indicator, relationship_type, impact_direction, impact_magnitude, impact_estimate, lag_months, evidence_basis, comparable_country, collected_by, collection_date, original_text, notes`

`parent_id` is populated only for `impact_link` rows (points at the `record_id` of the triggering event).

## Files

| File | Purpose |
|---|---|
| `ethiopia_fi_unified_data.csv` | The data (82 records: 41 observations, 3 targets, 13 events, 25 impact_links) |
| `reference_codes.csv` | Valid codes for each field |
| `SCHEMA.md` | This document |
