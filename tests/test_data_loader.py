import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import (
    load_unified_data, load_reference_codes, get_observations, get_events,
    get_impact_links, get_targets, events_with_impacts, get_indicator_series,
)

VALID_RECORD_TYPES = {"observation", "event", "impact_link", "target", "baseline", "forecast"}
VALID_PILLARS = {"ACCESS", "USAGE", "QUALITY", "AFFORDABILITY", "TRUST", "DEPTH", "GENDER", ""}


def test_data_loads():
    df = load_unified_data()
    assert len(df) > 0


def test_reference_codes_load():
    codes = load_reference_codes()
    assert "field" in codes.columns
    assert "code" in codes.columns


def test_record_types_are_valid():
    df = load_unified_data()
    assert set(df.record_type.unique()).issubset(VALID_RECORD_TYPES)


def test_events_have_no_pillar():
    df = load_unified_data()
    events = get_events(df)
    assert (events.pillar.fillna("") == "").all()


def test_observations_have_pillar():
    df = load_unified_data()
    obs = get_observations(df)
    assert (obs.pillar != "").all()
    assert set(obs.pillar.unique()).issubset(VALID_PILLARS)


def test_impact_links_have_parent_id():
    df = load_unified_data()
    impacts = get_impact_links(df)
    assert len(impacts) > 0
    assert (impacts.parent_id != "").all()


def test_impact_links_parent_ids_resolve_to_events():
    df = load_unified_data()
    impacts = get_impact_links(df)
    events = get_events(df)
    assert set(impacts.parent_id).issubset(set(events.record_id))


def test_targets_present():
    df = load_unified_data()
    targets = get_targets(df)
    assert len(targets) == 3


def test_events_with_impacts_join_succeeds():
    df = load_unified_data()
    merged = events_with_impacts(df)
    assert len(merged) == len(get_impact_links(df))


def test_get_indicator_series_returns_sorted_values():
    df = load_unified_data()
    series = get_indicator_series(df, "ACC_OWNERSHIP")
    assert len(series) >= 4
    assert series.observation_date.is_monotonic_increasing


def test_usg_digital_payment_indicator_present():
    """Regression guard: this indicator was missing from the original starter export."""
    df = load_unified_data()
    series = get_indicator_series(df, "USG_DIGITAL_PAYMENT")
    assert len(series) >= 1
