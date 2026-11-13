"""BharatPV Signal Dashboard — India-specific ADR signal detection.
Streamlit app. Run locally:  streamlit run app.py
Data files live in data/ (all derived from public FDA FAERS data + Indian
medical literature; see README.md). No server, no database, no API keys.
"""
import os
import pandas as pd
import plotly.express as px
import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

INDIA_COLS = ["drug", "event", "india_class", "india_confidence", "n_docs",
              "n_docs_india", "a_global", "a_india", "prr_global", "prr_india",
              "ror_india", "chi2_india", "prr_ratio_india_global"]

@st.cache_data
def load_india():
    df = pd.read_csv(os.path.join(DATA, "signals_india_2_0.csv"))
    return df.sort_values("a_india", ascending=False).reset_index(drop=True)

@st.cache_data
def load_pairs():
    return pd.read_parquet(os.path.join(DATA, "lit_drug_event_pairs.parquet"))

@st.cache_data
def load_global():
    return pd.read_csv(os.path.join(DATA, "signals_global_top500.csv"))

def filter_explorer(df, drug_q="", event_q="", min_india_cases=0, classes=None, signal_only=False):
    out = df
    if drug_q:
        out = out[out["drug"].str.contains(drug_q, case=False, na=False)]
    if event_q:
        out = out[out["event"].str.contains(event_q, case=False, na=False)]
    if min_india_cases:
        out = out[out["a_india"] >= min_india_cases]
    if classes:
        out = out[out["india_class"].isin(classes)]
    if signal_only:
        out = out[out["signal_global"] | out["signal_india"]]
    return out.sort_values(["a_india", "a_global"], ascending=False).reset_index(drop=True)

st.set_page_config(page_title="India ADR Signal Dashboard", layout="wide")
st.title("🇮🇳 India ADR Signal Dashboard")
st.caption("Pharmacovigilance signal detection — FDA FAERS (PS reports) + Indian medical literature. "
           "Research prototype, not a validated regulatory system.")

st.warning(
    "⚠️ **Disclaimer — please read:** These are **hypothesis-generating statistical signals** "
    "(PRR/ROR disproportionality), **not proven causation and not confirmed new side effects**. "
    "A high PRR only means a drug–event pair is reported more often than expected in FAERS. "
    "Any signal needs clinical review and further study before action. "
    "Do not use this dashboard to start, stop or change any treatment."
)

india = load_india()
lit = load_pairs()

c1, c2, c3, c4 = st.columns(4)
c1.metric("India signals (lit pairs)", len(india))
c2.metric("Reportable (a_india ≥ 10)", int((india["a_india"] >= 10).sum()))
c3.metric("India-only signals", int((india["india_class"] == "india_only_signal").sum()))
c4.metric("Stronger in India", int((india["india_class"] == "stronger_in_india").sum()))
st.caption("Data: FAERS PS drug–events 9,214,862 rows (India: 54,253) · literature pairs 90,787 "
           "(1,054 records + 274 full texts) · signal = PRR ≥ 2, χ² > 4, cases ≥ 3")

tab_main, tab_only, tab_stronger, tab_global, tab_explore = st.tabs([
    "🇮🇳 India Signals", "India-Only Signals", "Stronger-in-India Signals",
    "🌍 Global Signals", "🔍 Drug–Event Explorer",
])

with tab_main:
    st.subheader("India-specific signals — ranked by case count (a_india)")
    st.write("Ranking by **India case count, not raw PRR**: PRR is unstable when case "
             "counts are small, and raw-PRR leaderboards are dominated by indication "
             "artifacts. Only 22 of 133 India signals are reportable (a_india ≥ 10); "
             "the rest are marked weak and need more cases.")
    conf = st.radio("Confidence filter", ["All (133)", "Reportable — a_india ≥ 10 (22)",
                                          "Weak — a_india < 10 (111)"], horizontal=True)
    view = india
    if conf.startswith("Reportable"):
        view = india[india["a_india"] >= 10]
    elif conf.startswith("Weak"):
        view = india[india["a_india"] < 10]
    top10 = view.head(10)
    fig = px.bar(top10, x="a_india", y="drug", color="event", orientation="h",
                 title="Top 10 India signals by India case count",
                 labels={"a_india": "India cases (a_india)", "drug": "Drug"})
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=420)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(view[INDIA_COLS], use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download India signals as CSV", data=view.to_csv(index=False).encode("utf-8"),
                       file_name="india_signals.csv", mime="text/csv")

with tab_only:
    st.subheader("India-Only Signals (36)")
    st.write("Signals in Indian FAERS data that are **not** signals globally. "
             "These are the most India-specific findings — but check the case count: "
             "only 5 of the 36 have a_india ≥ 10.")
    only = india[india["india_class"] == "india_only_signal"]
    st.dataframe(only[INDIA_COLS], use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download India-only signals as CSV",
                       data=only.to_csv(index=False).encode("utf-8"),
                       file_name="india_only_signals.csv", mime="text/csv")

with tab_stronger:
    st.subheader("Stronger-in-India Signals (82)")
    st.write("Signals on **both** sides, but with a **higher PRR in India** than globally. "
             "Standout: **levetiracetam + parkinsonism** — 55 India cases, "
             "PRR_india 347 vs PRR_global 24.")
    stronger = india[india["india_class"] == "stronger_in_india"]
    fig2 = px.scatter(stronger, x="prr_global", y="prr_india", size="a_india",
                      hover_data=["drug", "event", "a_india"], log_x=True, log_y=True,
                      title="PRR in India vs PRR globally (log scale, bubble = India cases)",
                      labels={"prr_global": "PRR (global)", "prr_india": "PRR (India)"})
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(stronger[INDIA_COLS], use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download stronger-in-India signals as CSV",
                       data=stronger.to_csv(index=False).encode("utf-8"),
                       file_name="stronger_in_india_signals.csv", mime="text/csv")

with tab_global:
    st.subheader("Global Signals — ranked by chi-square")
    st.write("Top 500 global FAERS signals (PRR ≥ 2, χ² > 4, cases ≥ 10), ranked by "
             "**chi-square, not raw PRR**: the raw-PRR leaderboard is dominated by "
             "indication/device artifacts (e.g. Cetrotide + premature ovulation), "
             "so PRR alone is a misleading ranking.")
    glob = load_global()
    gq = st.text_input("Search global signals (drug or event)", key="gq")
    if gq:
        glob = glob[glob["drug"].str.contains(gq, case=False, na=False) |
                    glob["event"].str.contains(gq, case=False, na=False)]
    st.dataframe(glob[["drug", "event", "a", "prr", "ror", "chi2"]],
                 use_container_width=True, hide_index=True)

with tab_explore:
    st.subheader("Drug–Event Explorer")
    st.write("Search all 90,787 literature drug–event pairs with their FAERS statistics. "
             "Note: 91% of literature pairs never appear in FAERS at all — co-occurrence "
             "in a paper is not an association; the FAERS columns are the filter.")
    col_a, col_b = st.columns(2)
    dq = col_a.text_input("Drug name contains", key="dq", placeholder="e.g. metformin")
    eq = col_b.text_input("Event contains", key="eq", placeholder="e.g. rash")
    col_c, col_d, col_e = st.columns(3)
    min_cases = col_c.slider("Minimum India cases (a_india)", 0, 60, 0)
    classes = col_d.multiselect("India class",
                                ["india_only_signal", "stronger_in_india", "india_signal",
                                 "global_only_signal", "no_signal", "not_in_faers"],
                                default=[])
    sig_only = col_e.checkbox("Signals only (global or India)")
    res = filter_explorer(lit, dq, eq, min_cases, classes or None, sig_only)
    st.write(f"**{len(res):,} pairs** match.")
    show_cols = ["drug", "event", "india_class", "n_docs", "a_global", "a_india",
                 "prr_global", "prr_india", "ror_global", "ror_india",
                 "chi2_global", "chi2_india", "signal_global", "signal_india"]
    st.dataframe(res[show_cols], use_container_width=True, hide_index=True)

st.divider()
st.caption("Sources: FDA FAERS (alexcpn/fda-faers-parquet, CC0) · PubMed/NCBI · 8 Indian journals "
           "(Europe PMC OA full texts). Method: SciSpaCy BC5CDR NER + FAERS dictionary, "
           "PRR/ROR with Haldane–Anscombe +0.5 correction when a cell is 0.")
