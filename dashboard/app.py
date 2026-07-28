"""Ethiopia Financial Inclusion Forecasting Dashboard.

Run with: streamlit run dashboard/app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from src.data_loader import (
    load_unified_data, get_observations, get_events, get_impact_links,
    get_targets, events_with_impacts, get_indicator_series,
)

st.set_page_config(page_title="Ethiopia Financial Inclusion Forecast", layout="wide", page_icon="\U0001F1EA\U0001F1F9")

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"


@st.cache_data
def load_data():
    df = load_unified_data()
    return df


@st.cache_data
def load_forecast():
    fc = pd.read_csv(PROCESSED / "access_usage_forecast_2025_2027.csv", header=[0, 1], index_col=0)
    fc.columns = [f"{a}__{b}" for a, b in fc.columns]
    return fc


df = load_data()
obs = get_observations(df)
events = get_events(df)
impacts = get_impact_links(df)
targets = get_targets(df)
forecast = load_forecast()

INDICATOR_LABELS = (
    obs[["indicator_code", "indicator"]].drop_duplicates().set_index("indicator_code")["indicator"].to_dict()
)

PAGES = ["Overview", "Trends", "Forecasts", "Inclusion Projections"]
default_page = st.query_params.get("page", "Overview")
default_index = PAGES.index(default_page) if default_page in PAGES else 0

st.sidebar.title("Ethiopia Financial Inclusion")
st.sidebar.caption("Selam Analytics | Access & Usage Forecasting System")
page = st.sidebar.radio("Navigate", PAGES, index=default_index)
st.query_params["page"] = page

st.sidebar.markdown("---")
st.sidebar.download_button(
    "Download full dataset (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="ethiopia_fi_unified_data.csv",
    mime="text/csv",
)
st.sidebar.download_button(
    "Download forecast table (CSV)",
    data=forecast.to_csv().encode("utf-8"),
    file_name="access_usage_forecast_2025_2027.csv",
    mime="text/csv",
)

# =====================================================================
# OVERVIEW
# =====================================================================
if page == "Overview":
    st.title("Ethiopia Financial Inclusion — Overview")
    st.caption("Global Findex-defined Access & Usage indicators, tracked through cataloged policy/product events.")

    acc = get_indicator_series(df, "ACC_OWNERSHIP")
    mm = get_indicator_series(df, "ACC_MM_ACCOUNT")
    usg = get_indicator_series(df, "USG_DIGITAL_PAYMENT")
    crossover = get_indicator_series(df, "USG_CROSSOVER")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Account Ownership (Access)", f"{acc.value_numeric.iloc[-1]:.0f}%",
              f"+{acc.value_numeric.iloc[-1] - acc.value_numeric.iloc[-2]:.0f}pp since {acc.observation_date.iloc[-2].year}")
    c2.metric("Mobile Money Accounts", f"{mm.value_numeric.iloc[-1]:.2f}%",
              f"+{mm.value_numeric.iloc[-1] - mm.value_numeric.iloc[0]:.2f}pp since {mm.observation_date.iloc[0].year}")
    c3.metric("Digital Payment Adoption (Usage)", f"{usg.value_numeric.iloc[-1]:.0f}%", "2024 Findex")
    c4.metric("P2P / ATM Crossover Ratio", f"{crossover.value_numeric.iloc[-1]:.2f}",
              "P2P > ATM for the first time" if crossover.value_numeric.iloc[-1] > 1 else "ATM still leads")

    st.markdown("---")
    col1, col2 = st.columns([1.3, 1])

    with col1:
        st.subheader("Account Ownership growth by Findex period")
        acc_growth = acc.copy()
        acc_growth["year"] = acc_growth.observation_date.dt.year
        acc_growth["pp_growth"] = acc_growth.value_numeric.diff()
        acc_growth["years_elapsed"] = acc_growth.observation_date.dt.year.diff()
        acc_growth["pp_per_year"] = acc_growth.pp_growth / acc_growth.years_elapsed
        acc_growth = acc_growth.dropna(subset=["pp_growth"])
        fig = px.bar(acc_growth, x="year", y="pp_growth", text="pp_growth",
                     labels={"year": "Survey year", "pp_growth": "pp growth since prior survey"},
                     color="pp_per_year", color_continuous_scale="RdYlGn",
                     title="Deceleration is visible: +13pp -> +11pp -> +3pp")
        fig.update_traces(texttemplate="+%{text:.0f}pp", textposition="outside")
        st.plotly_chart(fig, width='stretch')

    with col2:
        st.subheader("Record composition")
        counts = df.record_type.value_counts().reset_index()
        counts.columns = ["record_type", "count"]
        fig2 = px.pie(counts, names="record_type", values="count", hole=0.45,
                      title=f"{len(df)} total records")
        st.plotly_chart(fig2, width='stretch')

    st.markdown("---")
    st.subheader("Registered vs. active usage gap")
    gap_data = pd.DataFrame({
        "metric": ["M-Pesa Registered", "M-Pesa 90-day Active", "Telebirr Registered"],
        "value_millions": [10.8, 7.1, 54.84],
    })
    fig3 = px.bar(gap_data, x="metric", y="value_millions", text="value_millions",
                  title="Registered user counts overstate functional usage",
                  labels={"value_millions": "Users (millions)"})
    fig3.update_traces(texttemplate="%{text:.1f}M", textposition="outside")
    st.plotly_chart(fig3, width='stretch')

    st.info(
        "**Key takeaway:** Access (account ownership) is decelerating (+3pp 2021-2024) while "
        "Usage indicators (mobile money accounts, P2P volume) are accelerating — the two pillars "
        "are decoupling. See the Trends and Forecasts pages for detail."
    )

# =====================================================================
# TRENDS
# =====================================================================
elif page == "Trends":
    st.title("Trends Explorer")
    st.caption("Interactive time series across all tracked indicators, with cataloged events overlaid.")

    pillars = sorted(obs.pillar.dropna().unique())
    sel_pillar = st.selectbox("Filter by pillar", ["All"] + pillars)
    pool = obs if sel_pillar == "All" else obs[obs.pillar == sel_pillar]
    codes = sorted(pool.indicator_code.unique())
    labels = [f"{c} — {INDICATOR_LABELS.get(c, '')}" for c in codes]
    code_map = dict(zip(labels, codes))

    default_codes = [l for l in labels if l.startswith("ACC_OWNERSHIP") or l.startswith("ACC_MM_ACCOUNT")]
    selected_labels = st.multiselect("Indicators to compare", labels, default=default_codes or labels[:2])
    selected_codes = [code_map[l] for l in selected_labels]

    min_date = obs.observation_date.min().date()
    max_date = pd.Timestamp("2027-12-31").date()
    date_range = st.slider("Date range", min_value=min_date, max_value=max_date,
                            value=(min_date, max_date))

    show_events = st.checkbox("Overlay cataloged events", value=True)

    if selected_codes:
        fig = go.Figure()
        for code in selected_codes:
            series = obs[(obs.indicator_code == code) & (obs.gender == "all") & (obs.location == "national")]
            series = series[(series.observation_date.dt.date >= date_range[0]) & (series.observation_date.dt.date <= date_range[1])]
            series = series.sort_values("observation_date")
            if len(series):
                fig.add_trace(go.Scatter(
                    x=series.observation_date, y=series.value_numeric, mode="lines+markers",
                    name=INDICATOR_LABELS.get(code, code),
                    hovertext=series.notes.fillna(""), hoverinfo="x+y+text+name",
                ))

        if show_events:
            evs = events[(events.observation_date.dt.date >= date_range[0]) & (events.observation_date.dt.date <= date_range[1])]
            for _, ev in evs.iterrows():
                fig.add_vline(x=ev.observation_date, line_dash="dash", line_color="grey", opacity=0.5)
                fig.add_annotation(x=ev.observation_date, y=1, yref="paper", showarrow=False,
                                    text=ev.indicator, textangle=-90, font=dict(size=9), yshift=10)

        fig.update_layout(title="Indicator trends", yaxis_title="Value", height=550,
                           legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig, width='stretch')
    else:
        st.warning("Select at least one indicator.")

    st.markdown("---")
    st.subheader("Channel comparison: P2P vs. ATM transaction volume")
    p2p = get_indicator_series(df, "USG_P2P_COUNT")
    atm = get_indicator_series(df, "USG_ATM_COUNT")
    comp = pd.concat([
        p2p.assign(channel="P2P")[["observation_date", "value_numeric", "channel"]],
        atm.assign(channel="ATM")[["observation_date", "value_numeric", "channel"]],
    ])
    comp["value_millions"] = comp.value_numeric / 1e6
    fig4 = px.line(comp, x="observation_date", y="value_millions", color="channel", markers=True,
                   title="P2P has overtaken ATM transaction volume (EthSwitch)",
                   labels={"value_millions": "Transactions (millions)", "observation_date": "Date"})
    st.plotly_chart(fig4, width='stretch')

    with st.expander("View underlying data"):
        st.dataframe(obs[["observation_date", "indicator", "indicator_code", "value_numeric",
                          "gender", "location", "source_name", "confidence"]].sort_values("observation_date"))

# =====================================================================
# FORECASTS
# =====================================================================
elif page == "Forecasts":
    st.title("Access & Usage Forecasts, 2025-2027")
    st.caption("Trend + event-augmented models. See notebooks/03_impact_modeling.ipynb and "
               "04_forecasting.ipynb for full methodology.")

    target = st.radio("Forecast target", ["Access (Account Ownership %)", "Usage (Digital Payment Adoption %)"], horizontal=True)
    scenario_view = st.selectbox("Scenario view", ["All scenarios", "Optimistic", "Base", "Pessimistic"])

    cols = [c for c in forecast.columns if c.startswith(target)]
    sub = forecast[cols].copy()
    sub.columns = [c.split("__")[1] for c in sub.columns]

    anchor_year = 2024
    anchor_value = 49.0 if target.startswith("Access") else 35.0

    fig = go.Figure()
    plot_scn = ["optimistic", "base", "pessimistic"] if scenario_view == "All scenarios" else [scenario_view.lower()]
    colors = {"optimistic": "#2ca02c", "base": "#4C72B0", "pessimistic": "#C44E52"}
    for scn in plot_scn:
        y = [anchor_value] + list(sub[scn])
        fig.add_trace(go.Scatter(x=[anchor_year, 2025, 2026, 2027], y=y, mode="lines+markers",
                                  name=scn.capitalize(), line=dict(color=colors[scn], dash="dash")))
    if scenario_view == "All scenarios":
        fig.add_trace(go.Scatter(
            x=[2025, 2026, 2027] + [2027, 2026, 2025], y=list(sub.optimistic) + list(sub.pessimistic[::-1]),
            fill="toself", fillcolor="rgba(76,114,176,0.1)", line=dict(width=0), name="Scenario range", showlegend=False,
        ))

    if target.startswith("Access"):
        nfis = targets[targets.indicator_code == "ACC_OWNERSHIP"]
        if len(nfis):
            fig.add_trace(go.Scatter(x=[nfis.observation_date.iloc[0].year], y=[nfis.value_numeric.iloc[0]],
                                      mode="markers", marker=dict(color="red", size=16, symbol="star"),
                                      name="NFIS-II target (70%, 2025)"))

    fig.update_layout(title=f"{target}: 2025-2027 forecast", yaxis_title="%", height=500)
    st.plotly_chart(fig, width='stretch')

    st.subheader("Forecast table")
    display_table = sub.copy()
    display_table.index.name = "Year"
    st.dataframe(display_table.style.format("{:.1f}"))

    st.markdown("### Key projected milestones")
    st.markdown(
        "- **Access, base case:** 54% (2025) -> 57% (2026) -> **60% (2027)** — NFIS-II's 70% target "
        "is missed on its original 2025 timeline under every scenario except the optimistic one, "
        "which lands almost exactly on 70% by 2027 (~2 years late).\n"
        "- **Usage, base case:** 39% (2025) -> 43% (2026) -> **47% (2027)** — outpaces Access in every "
        "scenario, driven by EthioPay's instant-payment rollout (Dec 2025) and M-Pesa/EthSwitch "
        "interoperability (Oct 2025).\n"
        "- **Largest uncertainty:** the Usage forecast rests on a single 2024 data point — there is "
        "no historical trend to validate against, so treat the scenario spread as the honest signal, "
        "not the point estimate."
    )

    with st.expander("Event -> indicator association matrix (Task 3)"):
        ei = events_with_impacts(df)
        st.dataframe(ei[["event_name", "event_category", "pillar", "related_indicator",
                         "impact_direction", "impact_magnitude", "evidence_basis"]])

# =====================================================================
# INCLUSION PROJECTIONS
# =====================================================================
elif page == "Inclusion Projections":
    st.title("Inclusion Projections & Policy Questions")

    scenario = st.select_slider("Scenario", options=["Pessimistic", "Base", "Optimistic"], value="Base")
    scn_key = scenario.lower()

    acc_2027 = forecast[f"Access (Account Ownership %)__{scn_key}"].loc[2027]
    usg_2027 = forecast[f"Usage (Digital Payment Adoption %)__{scn_key}"].loc[2027]
    nfis_target = 70.0

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Progress toward NFIS-II Access target (70% by 2025)")
        progress = min(1.0, acc_2027 / nfis_target)
        st.progress(progress, text=f"{acc_2027:.1f}% of {nfis_target:.0f}% target projected by 2027 ({scenario} scenario)")
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number", value=acc_2027,
            title={"text": "Account Ownership, 2027 projection"},
            gauge={"axis": {"range": [0, 100]},
                   "bar": {"color": "#4C72B0"},
                   "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.9, "value": nfis_target}},
        ))
        fig_g.update_layout(height=320)
        st.plotly_chart(fig_g, width='stretch')

    with col2:
        st.subheader("Usage projection, 2027")
        fig_g2 = go.Figure(go.Indicator(
            mode="gauge+number", value=usg_2027,
            title={"text": "Digital Payment Adoption, 2027 projection"},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#55A868"}},
        ))
        fig_g2.update_layout(height=320)
        st.plotly_chart(fig_g2, width='stretch')

    st.markdown("---")
    st.subheader("Answers to the consortium's key questions")

    with st.expander("What drives financial inclusion in Ethiopia?", expanded=True):
        st.markdown(
            "Mobile connectivity and digital rails (4G coverage nearly doubling, Telebirr/M-Pesa, "
            "EthioPay) are the strongest drivers of **Usage** growth. **Access** growth is driven more "
            "by digital ID (Fayda) reducing account-opening friction and NFIS-II's multi-channel policy "
            "push — but has decelerated sharply since bank accounts were already low-friction to open "
            "(Market Nuance D) and the easy-to-reach population is largely saturated."
        )

    with st.expander("How do events like product launches, policy changes, and infrastructure investments affect outcomes?"):
        st.markdown(
            "See the event -> indicator association matrix (Forecasts page). Product launches "
            "(Telebirr, M-Pesa) show large, fast, well-evidenced effects on mobile money account "
            "rates specifically, but only modest indirect effects on overall account ownership. "
            "Infrastructure (Fayda, EthioPay) shows slower-building but potentially larger effects "
            "further out. Policy/regulation effects (NFIS-II, the Fayda banking mandate) are the "
            "most diffuse and uncertain — the mandate is explicitly modeled as double-edged."
        )

    with st.expander("How did financial inclusion change in 2025, and how will it look in 2026-2027?"):
        st.markdown(
            f"Under the **{scenario}** scenario: Account Ownership reaches **{acc_2027:.1f}%** and "
            f"Digital Payment Adoption reaches **{usg_2027:.1f}%** by 2027. Usage is projected to grow "
            "faster than Access in every scenario we modeled, continuing the decoupling already visible "
            "in the P2P/ATM crossover and mobile money growth data."
        )

    st.markdown("---")
    st.caption(
        "Data: Global Findex, IMF Financial Access Survey, Ethio Telecom, Safaricom, EthSwitch, NBE, "
        "GSMA, Fayda/NIDP. Full sourcing and confidence ratings in data_enrichment_log.md. "
        "Forecasts carry substantial uncertainty given sparse historical data (4-5 points per indicator) "
        "— treat scenario ranges, not point estimates, as the primary output."
    )
