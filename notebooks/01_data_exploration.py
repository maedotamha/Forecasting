# %% [markdown]
# # Task 1: Data Exploration — Understanding the Unified Schema
#
# Ethiopia Financial Inclusion Forecasting — Selam Analytics
#
# Confirms all three starter files load correctly and walks through the
# unified schema: how `record_type` determines whether `category` or `pillar`
# is populated, how `impact_link` rows connect to events via `parent_id`, and
# what's actually in the enriched dataset. See `data_enrichment_log.md` for
# the full account of what was added and why.

# %%
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd().parent))

import pandas as pd

from src.data_loader import (
    load_unified_data, load_reference_codes, get_observations, get_events,
    get_impact_links, get_targets, events_with_impacts,
)

df = load_unified_data()
codes = load_reference_codes()
print(f"Unified dataset: {len(df)} records, {len(df.columns)} columns")
print(f"Reference codes: {len(codes)} valid (field, code) pairs")

# %% [markdown]
# ## 1. Record type breakdown

# %%
df.record_type.value_counts()

# %% [markdown]
# ## 2. The schema's key design principle, verified in the data
#
# `event` rows should have `category` set and `pillar` empty (no pre-
# assignment of what dimension an event affects). `observation`/`target`/
# `impact_link` rows should have `pillar` set.

# %%
events = get_events(df)
print("Events with a non-empty pillar (should be 0):", (events.pillar.fillna("") != "").sum())
print("Events with a non-empty category (should be all):", (events.category.fillna("") != "").sum())

obs = get_observations(df)
print("Observations with an empty pillar (should be 0):", (obs.pillar.fillna("") == "").sum())

# %% [markdown]
# ## 3. Unique indicators and their coverage

# %%
coverage = (
    obs.groupby(["pillar", "indicator_code", "indicator"])
    .agg(n_observations=("value_numeric", "count"),
         first_date=("observation_date", "min"),
         last_date=("observation_date", "max"))
    .reset_index()
    .sort_values(["pillar", "indicator_code"])
)
coverage

# %% [markdown]
# ## 4. The event catalog

# %%
events[["record_id", "category", "indicator", "observation_date", "source_type", "confidence"]].sort_values("observation_date")

# %% [markdown]
# ## 5. impact_link -> event join (parent_id)
#
# This is the join pattern used throughout Tasks 2-4: every `impact_link`
# points back to the event that triggered it via `parent_id`.

# %%
ei = events_with_impacts(df)
print(f"{len(ei)} impact_links resolve cleanly to their parent event")
ei[["event_name", "event_category", "related_indicator", "pillar", "impact_direction", "impact_magnitude"]].head(8)

# %% [markdown]
# ## 6. Targets

# %%
get_targets(df)[["indicator", "indicator_code", "value_numeric", "observation_date", "source_name"]]

# %% [markdown]
# ## Summary
#
# All three files (`ethiopia_fi_unified_data.csv`, `reference_codes.csv`, and
# the derived helpers in `src/data_loader.py`) load and cross-reference
# correctly. The schema's core principle — events stay neutral, impact_links
# carry the interpretation — holds throughout the enriched 82-record dataset.
# Detailed exploratory analysis continues in `02_eda.ipynb`.
