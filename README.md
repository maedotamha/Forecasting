# Forecasting Financial Inclusion in Ethiopia

A forecasting system for Ethiopia's Global Findex-defined financial inclusion indicators — **Access** (Account Ownership Rate) and **Usage** (Digital Payment Adoption Rate) — built around a unified events/observations/impact-links dataset, an event-impact model, and Access/Usage forecasts for 2025-2027.

Built for the Selam Analytics financial inclusion forecasting challenge.

## Project structure

```
ethiopia-fi-forecast/
├── data/
│   ├── raw/                      # ethiopia_fi_unified_data.csv, reference_codes.csv, SCHEMA.md
│   └── processed/                # analysis-ready extracts (indicator series, matrices)
├── notebooks/
│   ├── 01_data_exploration.ipynb # Task 1: schema understanding
│   ├── 02_eda.ipynb              # Task 2: exploratory data analysis
│   ├── 03_impact_modeling.ipynb  # Task 3: event impact modeling
│   └── 04_forecasting.ipynb      # Task 4: Access & Usage forecasts 2025-2027
├── src/
│   ├── build_dataset.py          # reproducible construction of the unified dataset
│   └── data_loader.py            # shared data-access helpers
├── dashboard/
│   └── app.py                    # Streamlit dashboard (Task 5)
├── tests/                        # pytest suite (schema + loader checks)
├── reports/
│   ├── figures/                  # saved chart PNGs used by the reports
│   ├── Interim_Report.md
│   └── Final_Report.md
├── data_enrichment_log.md        # Task 1 deliverable: what we added/corrected and why
└── requirements.txt
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows (PowerShell: .venv\Scripts\Activate.ps1)
pip install -r requirements.txt
```

## Running the notebooks

```bash
jupyter notebook notebooks/
```
Run in order: `01_data_exploration` → `02_eda` → `03_impact_modeling` → `04_forecasting`.

## Running the dashboard

```bash
streamlit run dashboard/app.py
```
Opens at `http://localhost:8501`. Pages: **Overview**, **Trends**, **Forecasts**, **Inclusion Projections**.

## Running tests

```bash
pytest tests/ -v
```

## Data

The starter dataset uses a unified schema (`record_type` = `observation` | `event` | `impact_link` | `target`) documented in [`data/raw/SCHEMA.md`](data/raw/SCHEMA.md). Events are deliberately **not** pre-assigned to a pillar — their effects on specific indicators are captured through `impact_link` records instead, to avoid baking interpretation into the raw data.

The original export was missing the `impact_link` sheet (14 rows) entirely; we reconstructed it (25 rows, covering more events than the original 10) following the schema rules and using comparable-country evidence per Task 3's methodology, plus added 11 new observations and 3 new events sourced from public data (Global Findex, IMF FAS, NBE/EthSwitch, GSMA, Fayda program updates). Full details, sources, and data-quality caveats are in [`data_enrichment_log.md`](data_enrichment_log.md).

## Team / Attribution

Analysis, modeling, and dashboard: Maedot Amha, for the Selam Analytics Ethiopia Financial Inclusion Forecasting challenge (tutors: Kerod, Mahbubah, Feven).
