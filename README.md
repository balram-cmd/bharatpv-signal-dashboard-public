# BharatPV Signal Dashboard — India ADR Signal Detection

An interactive dashboard that shows **India-specific adverse drug reaction (ADR)
signals** found by comparing Indian medical literature with the FDA FAERS
spontaneous-reporting database.

## What it does

- **India Signals** — 133 India-specific signals, ranked by India case count
  (not raw PRR, which is unstable at small case counts). 22 are reportable
  (10 or more India cases); the rest are marked weak.
- **India-Only Signals** (36) — signals in Indian data that are not signals globally.
- **Stronger-in-India Signals** (82) — signals on both sides with a higher PRR in India.
  Standout: levetiracetam + parkinsonism (55 India cases, PRR 347 in India vs 24 globally).
- **Global Signals** — top 500 global FAERS signals, ranked by chi-square.
- **Drug–Event Explorer** — search all 90,787 literature drug–event pairs with
  their PRR, ROR, chi-square and case counts (global + India).
- **CSV export** — download the India signals tables from the dashboard.

## How to run it locally

You need Python 3.11 or newer on your computer.

1. Download this repository (Code → Download ZIP) and unzip it, or clone it:
   `git clone https://github.com/<your-username>/bharatpv-signal-dashboard.git`
2. Open a terminal in the folder and install the needed libraries:
   `pip install -r requirements.txt`
3. Start the app:
   `streamlit run app.py`
4. Your browser opens at `http://localhost:8501` with the dashboard.

No API keys, no database, no accounts are needed to run it.

## Data sources

- **FDA FAERS** — `alexcpn/fda-faers-parquet` (CC0, public domain):
  9,214,862 primary-suspect drug–event rows; 54,253 India rows (`india_any`).
- **PubMed / NCBI** — 744 India-focused ADR articles (2015–2025).
- **8 Indian medical journals** — 310 ADR records + 274 open-access full texts
  (Europe PMC).
- Signals computed with PRR/ROR and Pearson chi-square; signal = PRR ≥ 2,
  chi-square > 4, cases ≥ 3 (Evans et al. standard), with a +0.5 correction
  when a contingency-table cell is 0.

## Disclaimer — please read

These are **hypothesis-generating statistical signals** (PRR/ROR
disproportionality), **not proven causation and not confirmed new side effects**.
A high PRR only means a drug–event pair is reported more often than expected.
Any signal needs clinical review and further study before action. This is a
research and decision-support prototype, not a validated regulatory
pharmacovigilance system. Do not use it to start, stop or change any treatment.

## Files in this repository

- `app.py` — the Streamlit dashboard (everything the app needs).
- `data/signals_india_2_0.csv` — the 133 India signals.
- `data/lit_drug_event_pairs.parquet` — all 90,787 literature drug–event pairs
  with FAERS statistics.
- `data/signals_global_top500.csv` — top 500 global signals by chi-square.
- `requirements.txt` — Python libraries the app needs.
