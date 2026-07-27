"""Shared data access helpers for the Ethiopia Financial Inclusion project."""
from pathlib import Path
import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
DATA_PATH = RAW_DIR / "ethiopia_fi_unified_data.csv"
CODES_PATH = RAW_DIR / "reference_codes.csv"

DATE_COLS = ["observation_date", "period_start", "period_end", "collection_date"]


def load_unified_data(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in DATE_COLS:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    numeric_cols = ["value_numeric", "impact_estimate", "lag_months"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_reference_codes(path: Path = CODES_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


def get_observations(df: pd.DataFrame, pillar: str | None = None) -> pd.DataFrame:
    obs = df[df.record_type == "observation"].copy()
    if pillar:
        obs = obs[obs.pillar == pillar]
    return obs.sort_values("observation_date")


def get_targets(df: pd.DataFrame) -> pd.DataFrame:
    return df[df.record_type == "target"].copy().sort_values("observation_date")


def get_events(df: pd.DataFrame) -> pd.DataFrame:
    return df[df.record_type == "event"].copy().sort_values("observation_date")


def get_impact_links(df: pd.DataFrame) -> pd.DataFrame:
    return df[df.record_type == "impact_link"].copy()


def events_with_impacts(df: pd.DataFrame) -> pd.DataFrame:
    """Join impact_link rows to their parent event for a flat event-effect table."""
    events = get_events(df)
    impacts = get_impact_links(df)
    merged = impacts.merge(
        events,
        left_on="parent_id",
        right_on="record_id",
        suffixes=("_impact", "_event"),
    )
    cols = [
        "record_id_event", "indicator_event", "category_event", "observation_date_event",
        "record_id_impact", "pillar_impact", "related_indicator_impact", "relationship_type_impact",
        "impact_direction_impact", "impact_magnitude_impact", "impact_estimate_impact", "lag_months_impact",
        "evidence_basis_impact", "comparable_country_impact", "notes_impact",
    ]
    return merged[cols].rename(columns={
        "record_id_event": "event_id",
        "indicator_event": "event_name",
        "category_event": "event_category",
        "observation_date_event": "event_date",
        "record_id_impact": "impact_id",
        "pillar_impact": "pillar",
        "related_indicator_impact": "related_indicator",
        "relationship_type_impact": "relationship_type",
        "impact_direction_impact": "impact_direction",
        "impact_magnitude_impact": "impact_magnitude",
        "impact_estimate_impact": "impact_estimate",
        "lag_months_impact": "lag_months",
        "evidence_basis_impact": "evidence_basis",
        "comparable_country_impact": "comparable_country",
        "notes_impact": "notes",
    })


def get_indicator_series(df: pd.DataFrame, indicator_code: str, gender: str = "all",
                          location: str = "national") -> pd.DataFrame:
    obs = get_observations(df)
    series = obs[
        (obs.indicator_code == indicator_code)
        & (obs.gender == gender)
        & (obs.location == location)
    ]
    return series.sort_values("observation_date")[
        ["observation_date", "value_numeric", "source_name", "confidence", "notes"]
    ]
