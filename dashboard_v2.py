import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Presizing · Operations Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────
# DESIGN SYSTEM — Industrial precision theme
# Palette: deep slate bg, warm white text, amber accent, emerald positive, rose negative
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Sora:wght@300;400;600;700&display=swap');

  :root {
    --bg:        #0f1117;
    --surface:   #181c27;
    --border:    #252a3a;
    --amber:     #f5a623;
    --amber-dim: #7a4f0a;
    --emerald:   #34d399;
    --rose:      #fb7185;
    --slate:     #94a3b8;
    --white:     #e8eaf2;
    --card-h:    border-top: 3px solid var(--amber);
  }

  html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--white) !important;
    font-family: 'Sora', sans-serif !important;
  }

  [data-testid="stHeader"] { background: transparent !important; }

  /* Tab bar */
  [data-testid="stTabs"] > div:first-child {
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
  }
  [data-testid="stTabs"] button {
    font-family: 'Sora', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--slate) !important;
    padding: 10px 24px !important;
    border-radius: 0 !important;
    border: none !important;
    background: transparent !important;
    transition: color 0.2s;
  }
  [data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--amber) !important;
    border-bottom: 2px solid var(--amber) !important;
    background: transparent !important;
  }

  /* Selectboxes / radios */
  [data-testid="stSelectbox"] label,
  [data-testid="stRadio"] label,
  .stSelectbox label { color: var(--slate) !important; font-size: 0.72rem !important; letter-spacing: 0.05em; text-transform: uppercase; }
  [data-testid="stSelectbox"] > div > div { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 6px !important; color: var(--white) !important; }

  /* DataFrames */
  [data-testid="stDataFrame"] { background: var(--surface) !important; border-radius: 8px !important; border: 1px solid var(--border) !important; overflow: hidden; }
  [data-testid="stDataFrame"] table { font-family: 'DM Mono', monospace !important; font-size: 0.75rem !important; }
  [data-testid="stDataFrame"] th { background: #1e2435 !important; color: var(--amber) !important; font-weight: 500 !important; }
  [data-testid="stDataFrame"] tr:nth-child(even) td { background: #181c27 !important; }

  /* Metrics */
  [data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: 3px solid var(--amber) !important;
    border-radius: 8px !important;
    padding: 16px 20px !important;
  }
  [data-testid="stMetricLabel"] { color: var(--slate) !important; font-size: 0.7rem !important; text-transform: uppercase !important; letter-spacing: 0.07em !important; }
  [data-testid="stMetricValue"] { color: var(--white) !important; font-family: 'DM Mono', monospace !important; font-size: 1.5rem !important; font-weight: 500 !important; }
  [data-testid="stMetricDelta"] svg { display: none !important; }
  [data-testid="stMetricDelta"] > div { font-size: 0.72rem !important; font-family: 'DM Mono', monospace !important; }

  /* Divider */
  hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

  /* Info boxes */
  [data-testid="stInfo"] { background: #1a2236 !important; border-left: 3px solid var(--amber) !important; color: var(--slate) !important; border-radius: 4px; font-size: 0.8rem; }

  /* Radio inline */
  [data-testid="stRadio"] > div { gap: 6px !important; }
  [data-testid="stRadio"] > div > label { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 6px !important; padding: 6px 14px !important; color: var(--slate) !important; font-size: 0.75rem !important; transition: all 0.15s; }
  [data-testid="stRadio"] > div > label:has(input:checked) { border-color: var(--amber) !important; color: var(--amber) !important; background: rgba(245,166,35,0.08) !important; }

  /* Section headings via markdown */
  .section-title {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--amber);
    margin-bottom: 10px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px;
  }
  .kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-top: 3px solid var(--amber);
    border-radius: 8px;
    padding: 18px 22px;
    margin-bottom: 10px;
  }
  .kpi-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--slate); margin-bottom: 4px; }
  .kpi-value { font-family: 'DM Mono', monospace; font-size: 1.6rem; font-weight: 500; color: var(--white); }
  .kpi-delta { font-family: 'DM Mono', monospace; font-size: 0.7rem; margin-top: 4px; }
  .kpi-delta.up   { color: var(--emerald); }
  .kpi-delta.down { color: var(--rose); }
  .kpi-delta.neu  { color: var(--slate); }

  .insight-tag {
    display: inline-block;
    background: rgba(245,166,35,0.1);
    border: 1px solid var(--amber-dim);
    color: var(--amber);
    font-size: 0.7rem;
    font-family: 'DM Mono', monospace;
    padding: 3px 10px;
    border-radius: 100px;
    margin: 3px 3px 3px 0;
  }
  .alert-card {
    background: rgba(251,113,133,0.07);
    border: 1px solid rgba(251,113,133,0.3);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 0.78rem;
    color: var(--rose);
  }
  .good-card {
    background: rgba(52,211,153,0.07);
    border: 1px solid rgba(52,211,153,0.3);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 0.78rem;
    color: var(--emerald);
  }
  .page-header {
    display: flex; align-items: baseline; gap: 16px;
    margin-bottom: 20px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 14px;
  }
  .page-header h1 {
    font-family: 'Sora', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--white);
    margin: 0;
    letter-spacing: -0.01em;
  }
  .page-header span {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: var(--slate);
  }
  .badge {
    display:inline-block; padding:2px 8px; border-radius:4px;
    font-size:0.65rem; font-family:'DM Mono',monospace; font-weight:500;
    background:rgba(245,166,35,0.15); color:var(--amber); letter-spacing:0.04em;
  }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# PLOTLY THEME
# ─────────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#181c27",
    font=dict(family="DM Mono, monospace", color="#94a3b8", size=11),
    title_font=dict(family="Sora, sans-serif", color="#e8eaf2", size=13),
    xaxis=dict(gridcolor="#252a3a", linecolor="#252a3a", tickfont=dict(size=10)),
    yaxis=dict(gridcolor="#252a3a", linecolor="#252a3a", tickfont=dict(size=10)),
    margin=dict(l=20, r=20, t=44, b=20),
    hovermode="x unified",
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
)
AMBER = "#f5a623"
EMERALD = "#34d399"
ROSE = "#fb7185"
BLUE = "#60a5fa"
PURPLE = "#a78bfa"
SLATE = "#94a3b8"

COLOR_SEQ = [AMBER, BLUE, EMERALD, PURPLE, ROSE, "#f9a8d4", "#fcd34d", "#6ee7b7"]

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_csv(filename):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    return None

def apply_plot_theme(fig, height=380):
    fig.update_layout(**PLOT_LAYOUT, height=height)
    return fig

def pct_delta(current, previous):
    """Returns (value_str, delta_str, direction)"""
    if pd.isna(current):
        return "N/A", "", "neu"
    v_str = f"{current:,.1f}"
    if pd.isna(previous) or previous == 0:
        return v_str, "", "neu"
    d = ((current - previous) / abs(previous)) * 100
    direction = "up" if d >= 0 else "down"
    return v_str, f"{d:+.1f}% vs prev", direction

def num_delta(current, previous, fmt=".0f"):
    if pd.isna(current):
        return "N/A", "", "neu"
    v_str = f"{current:,.{fmt[1:]}}" if fmt != ".0f" else f"{int(current):,}"
    if pd.isna(previous):
        return v_str, "", "neu"
    d = current - previous
    direction = "up" if d >= 0 else "down"
    return v_str, f"{d:+,.1f} vs prev", direction

def kpi_html(label, value, delta="", direction="neu"):
    delta_html = f'<div class="kpi-delta {direction}">{delta}</div>' if delta else ""
    return f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      {delta_html}
    </div>
    """

def summarize_boundaries(series):
    vals = series.dropna().astype(str).str.strip()
    vals = vals[vals != ""]
    if vals.empty:
        return "", ""
    counts = vals.value_counts()
    top_3 = ", ".join(counts.head(3).index.tolist())
    def sort_key(x):
        try: return float(x)
        except: return float("inf")
    all_sorted = ", ".join(sorted(vals.unique().tolist(), key=sort_key))
    return top_3, all_sorted

# ─────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────
runs    = load_csv("runs_raw.csv")
batches = load_csv("batches_raw.csv")
changes = load_csv("changes_raw.csv")
downtime = load_csv("downtime_raw.csv")

if runs is None:
    st.error("runs_raw.csv not found.")
    st.stop()

# ─────────────────────────────────────────────────────────────
# CLEAN RUNS
# ─────────────────────────────────────────────────────────────
runs["run_date_raw"] = runs["run_date"].astype(str).str.strip()
d1 = pd.to_datetime(runs["run_date_raw"], dayfirst=True, errors="coerce")
d2 = pd.to_datetime(runs["run_date_raw"], yearfirst=True, errors="coerce")
runs["run_date"] = d1.fillna(d2)
runs = runs.dropna(subset=["run_date"]).copy()

for col in ["receival_date_min", "receival_date_max"]:
    if col in runs.columns:
        runs[col] = pd.to_datetime(runs[col].astype(str).str.strip(), dayfirst=True, errors="coerce")

numeric_cols_runs = [
    "batch_id","bins_run","retip","premium_rate","c1_color_rate","c1_quality_rate",
    "c2_color_rate","c2_quality_rate","no_color_rate","juice_rate",
    "test_drop_count","test_drop_kg","Speed_12","Speed_34","Speed_56","full_speed"
]
for col in numeric_cols_runs:
    if col in runs.columns:
        runs[col] = pd.to_numeric(runs[col], errors="coerce")

speed_cols = [c for c in ["Speed_12","Speed_34","Speed_56","full_speed"] if c in runs.columns]

for col in ["start_time","end_time"]:
    if col in runs.columns:
        runs[col] = runs[col].astype(str).str.strip()

if all(c in runs.columns for c in ["run_date","start_time","end_time"]):
    runs["start_dt"] = pd.to_datetime(
        runs["run_date"].dt.strftime("%Y-%m-%d") + " " + runs["start_time"], errors="coerce")
    runs["end_dt"] = pd.to_datetime(
        runs["run_date"].dt.strftime("%Y-%m-%d") + " " + runs["end_time"], errors="coerce")
    mask = runs["end_dt"] < runs["start_dt"]
    runs.loc[mask, "end_dt"] += pd.Timedelta(days=1)
    runs["run_hours"] = (runs["end_dt"] - runs["start_dt"]).dt.total_seconds() / 3600
    runs["total_bins_with_retip"] = runs["bins_run"].fillna(0) + runs["retip"].fillna(0)
    runs["bins_per_hour_row"] = runs["total_bins_with_retip"] / runs["run_hours"]
    runs.loc[runs["run_hours"] <= 0, "bins_per_hour_row"] = pd.NA
else:
    runs["run_hours"] = pd.NA
    runs["total_bins_with_retip"] = runs["bins_run"].fillna(0) + runs["retip"].fillna(0)
    runs["bins_per_hour_row"] = pd.NA

# ─────────────────────────────────────────────────────────────
# CLEAN BATCHES
# ─────────────────────────────────────────────────────────────
if batches is not None:
    for col in ["receival_date_min","receival_date_max"]:
        if col in batches.columns:
            batches[col] = pd.to_datetime(batches[col].astype(str).str.strip(), dayfirst=True, errors="coerce")
    for col in ["batch_id","premium","premium%"]:
        if col in batches.columns:
            batches[col] = pd.to_numeric(batches[col], errors="coerce")

# ─────────────────────────────────────────────────────────────
# CLEAN CHANGES
# ─────────────────────────────────────────────────────────────
if changes is not None:
    changes = changes.drop(columns=[c for c in changes.columns if c.startswith("Unnamed")], errors="ignore")
    if "change_time" in changes.columns:
        changes["change_time"] = pd.to_datetime(changes["change_time"], errors="coerce")
    for col in ["boundary_before","boundary_after"]:
        if col in changes.columns:
            changes[col] = pd.to_numeric(changes[col], errors="coerce")
    for col in ["reason","mode","check_class","action","variety","sensitivity","accuracy"]:
        if col in changes.columns:
            changes[col] = (changes[col].fillna("").astype(str).str.strip().replace("", pd.NA))

# ─────────────────────────────────────────────────────────────
# CLEAN DOWNTIME
# ─────────────────────────────────────────────────────────────
if downtime is not None:
    if "run_date" in downtime.columns:
        downtime["run_date_raw"] = downtime["run_date"].astype(str).str.strip()
        dt1 = pd.to_datetime(downtime["run_date_raw"], dayfirst=True, errors="coerce")
        dt2 = pd.to_datetime(downtime["run_date_raw"], yearfirst=True, errors="coerce")
        downtime["run_date"] = dt1.fillna(dt2)
    if "duration_hours" in downtime.columns:
        downtime["duration_hours"] = pd.to_numeric(downtime["duration_hours"], errors="coerce")
    for col in ["downtime_area","downtime_reason"]:
        if col in downtime.columns:
            downtime[col] = (downtime[col].fillna("").astype(str).str.strip().replace("", pd.NA))

# ─────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────
latest_date = runs["run_date"].max()
date_str = latest_date.strftime("%d %b %Y") if pd.notna(latest_date) else "N/A"

st.markdown(f"""
<div class="page-header">
  <h1>🍎 Presizing Operations</h1>
  <span>Updated {date_str} &nbsp;·&nbsp; {len(runs):,} runs recorded</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────
tab_summary, tab_quality, tab_mode, tab_operators = st.tabs([
    "📊  Summary", "🍏  Quality", "⚙️  Mode", "👷  Operators"
])

# ═══════════════════════════════════════════════════════════════
# SUMMARY TAB
# ═══════════════════════════════════════════════════════════════
with tab_summary:

    # ── Period selector ─────────────────────────────────────
    fc1, fc2, fc3 = st.columns([1, 1, 3])
    with fc1:
        period_choice = st.radio("View by", ["Yearly","Monthly","Weekly"], horizontal=True)
    with fc2:
        pass  # spacer

    summary_df = runs.dropna(subset=["run_date"]).copy()

    def format_delta(current, previous, mode="number"):
        if pd.isna(current) or pd.isna(previous): return "N/A"
        if mode == "percent":
            if previous == 0: return "N/A"
            return f"{((current-previous)/previous)*100:+.1f}% vs prev"
        if mode == "float": return f"{current-previous:+.1f} vs prev"
        return f"{int(current-previous):+,.0f} vs prev"

    # ── Period slicing ───────────────────────────────────────
    if period_choice == "Yearly":
        summary_df["year"] = summary_df["run_date"].dt.year.astype(int)
        available_years = sorted(summary_df["year"].dropna().unique(), reverse=True)
        selected_year = st.selectbox("Year", available_years, key="s_year")
        chart_df = summary_df.groupby("year", as_index=False)["bins_run"].sum().sort_values("year")
        summary_filtered = summary_df[summary_df["year"] == selected_year].copy()
        selected_period_label = str(selected_year)
        prev_year = selected_year - 1
        previous_filtered = summary_df[summary_df["year"] == prev_year].copy()

    elif period_choice == "Monthly":
        summary_df["year"] = summary_df["run_date"].dt.year.astype(int)
        summary_df["month_num"] = summary_df["run_date"].dt.month
        summary_df["month_name"] = summary_df["run_date"].dt.strftime("%b")
        summary_df["month_label"] = summary_df["run_date"].dt.to_period("M").astype(str)
        available_years = sorted(summary_df["year"].dropna().unique(), reverse=True)
        selected_year = st.selectbox("Year", available_years, key="s_year_m")
        year_df = summary_df[summary_df["year"] == selected_year].copy()
        available_months = year_df["month_label"].dropna().drop_duplicates().sort_values().tolist()
        selected_month = st.selectbox("Month", ["All"] + available_months, key="s_month")
        chart_df = (summary_df.groupby(["year","month_num","month_name"], as_index=False)["bins_run"]
                    .sum().sort_values(["month_num","year"], ascending=[True, False]))
        if selected_month == "All":
            summary_filtered = year_df.copy()
            selected_period_label = f"{selected_year} (All)"
            previous_filtered = pd.DataFrame()
            prev_month = None
        else:
            summary_filtered = year_df[year_df["month_label"] == selected_month].copy()
            selected_period_label = selected_month
            idx = available_months.index(selected_month)
            prev_month = available_months[idx-1] if idx > 0 else None
            previous_filtered = year_df[year_df["month_label"] == prev_month].copy() if prev_month else pd.DataFrame()

    else:  # Weekly
        summary_df["month_label"] = summary_df["run_date"].dt.to_period("M").astype(str)
        summary_df["week_start"] = summary_df["run_date"] - pd.to_timedelta(summary_df["run_date"].dt.weekday, unit="D")
        summary_df["week_label"] = "W/C " + summary_df["week_start"].dt.strftime("%Y-%m-%d")
        available_months = summary_df["month_label"].dropna().drop_duplicates().sort_values().tolist()
        selected_month = st.selectbox("Month", ["All"] + available_months, key="s_month_w")
        month_df = summary_df.copy() if selected_month == "All" else summary_df[summary_df["month_label"] == selected_month].copy()
        available_weeks = month_df[["week_label","week_start"]].drop_duplicates().sort_values("week_start")["week_label"].tolist()
        selected_week = st.selectbox("Week", ["All"] + available_weeks, key="s_week")
        chart_df = month_df.groupby(["week_label","week_start"], as_index=False)["bins_run"].sum().sort_values("week_start")
        if selected_week == "All":
            summary_filtered = month_df.copy()
            selected_period_label = f"{selected_month} (All)" if selected_month != "All" else "All"
            previous_filtered = pd.DataFrame()
            prev_week = None
        else:
            summary_filtered = month_df[month_df["week_label"] == selected_week].copy()
            selected_period_label = selected_week
            idx = available_weeks.index(selected_week)
            prev_week = available_weeks[idx-1] if idx > 0 else None
            previous_filtered = month_df[month_df["week_label"] == prev_week].copy() if prev_week else pd.DataFrame()

    # ── Downtime filter ─────────────────────────────────────
    downtime_filtered = pd.DataFrame()
    current_downtime = prev_downtime = None
    if downtime is not None and "run_date" in downtime.columns:
        dtf = downtime.dropna(subset=["run_date"]).copy()
        if period_choice == "Yearly":
            dtf["year"] = dtf["run_date"].dt.year.astype(int)
            cur_dt = dtf[dtf["year"] == selected_year]
            prv_dt = dtf[dtf["year"] == prev_year]
        elif period_choice == "Monthly":
            dtf["year"] = dtf["run_date"].dt.year.astype(int)
            dtf["month_label"] = dtf["run_date"].dt.to_period("M").astype(str)
            cur_dt = dtf[dtf["month_label"] == selected_month] if selected_month != "All" else dtf[dtf["year"] == selected_year]
            prv_dt = dtf[dtf["month_label"] == prev_month] if (selected_month != "All" and prev_month) else pd.DataFrame()
        else:
            dtf["week_label"] = "W/C " + (dtf["run_date"] - pd.to_timedelta(dtf["run_date"].dt.weekday, unit="D")).dt.strftime("%Y-%m-%d")
            cur_dt = dtf[dtf["week_label"] == selected_week] if selected_week != "All" else dtf
            prv_dt = dtf[dtf["week_label"] == prev_week] if (selected_week != "All" and prev_week) else pd.DataFrame()
        downtime_filtered = cur_dt.copy()
        current_downtime = cur_dt["duration_hours"].sum() if "duration_hours" in cur_dt.columns else None
        prev_downtime = prv_dt["duration_hours"].sum() if ("duration_hours" in prv_dt.columns and not prv_dt.empty) else None

    # ── KPIs ────────────────────────────────────────────────
    cur_bins  = summary_filtered["bins_run"].sum() if "bins_run" in summary_filtered.columns else None
    prev_bins = previous_filtered["bins_run"].sum() if ("bins_run" in previous_filtered.columns and not previous_filtered.empty) else None

    cur_bph = prev_bph = None
    if "total_bins_with_retip" in summary_filtered.columns and "run_hours" in summary_filtered.columns:
        th = summary_filtered["run_hours"].sum()
        tb = summary_filtered["total_bins_with_retip"].sum()
        if pd.notna(th) and th > 0: cur_bph = tb / th
    if not previous_filtered.empty and "total_bins_with_retip" in previous_filtered.columns:
        th2 = previous_filtered["run_hours"].sum()
        tb2 = previous_filtered["total_bins_with_retip"].sum()
        if pd.notna(th2) and th2 > 0: prev_bph = tb2 / th2

    cur_retip  = summary_filtered["retip"].sum() if "retip" in summary_filtered.columns else None
    prev_retip = previous_filtered["retip"].sum() if ("retip" in previous_filtered.columns and not previous_filtered.empty) else None

    # NEW: efficiency % = bins_run / total_bins_with_retip (retip ratio insight)
    retip_ratio = None
    if cur_retip is not None and cur_bins is not None and (cur_bins + cur_retip) > 0:
        retip_ratio = (cur_retip / (cur_bins + cur_retip)) * 100

    # NEW: total run hours
    total_hours = summary_filtered["run_hours"].sum() if "run_hours" in summary_filtered.columns else None

    k1, k2, k3, k4, k5 = st.columns(5)

    v, d, dr = pct_delta(cur_bins, prev_bins)
    k1.markdown(kpi_html("Total Bins Run", f"{cur_bins:,.0f}" if cur_bins else "N/A", format_delta(cur_bins, prev_bins, "percent"), "up" if "+" in format_delta(cur_bins, prev_bins, "percent") else "down"), unsafe_allow_html=True)

    k2.markdown(kpi_html("Bins / Hour", f"{cur_bph:.1f}" if cur_bph else "N/A", format_delta(cur_bph, prev_bph, "float"), "up" if cur_bph and prev_bph and cur_bph >= prev_bph else "down"), unsafe_allow_html=True)

    k3.markdown(kpi_html("Total Retip", f"{int(cur_retip):,}" if cur_retip else "N/A", format_delta(cur_retip, prev_retip), "down" if cur_retip and prev_retip and cur_retip > prev_retip else "up"), unsafe_allow_html=True)

    k4.markdown(kpi_html("Downtime", f"{current_downtime:.2f} hrs" if current_downtime else "N/A", format_delta(current_downtime, prev_downtime, "float"), "down" if current_downtime and prev_downtime and current_downtime > prev_downtime else "up"), unsafe_allow_html=True)

    k5.markdown(kpi_html("Retip Rate", f"{retip_ratio:.1f}%" if retip_ratio else "N/A", "bins sent back for re-grading", "neu"), unsafe_allow_html=True)

    st.markdown("---")

    # ── Charts row ──────────────────────────────────────────
    main_left, main_right = st.columns([2.2, 1.4])

    with main_left:
        st.markdown('<div class="section-title">Throughput Trend</div>', unsafe_allow_html=True)

        if period_choice == "Yearly":
            fig = px.bar(chart_df, x="year", y="bins_run", color_discrete_sequence=[AMBER])
            fig.update_xaxes(type="category")
        elif period_choice == "Monthly":
            fig = px.line(chart_df, x="month_name", y="bins_run", color="year",
                markers=True, color_discrete_sequence=COLOR_SEQ,
                category_orders={"month_name": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]})
        else:
            fig = px.bar(chart_df, x="week_label", y="bins_run", color_discrete_sequence=[AMBER])

        fig.update_traces(hovertemplate="%{y:,.0f} bins")
        apply_plot_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    with main_right:
        st.markdown(f'<div class="section-title">Variety Split — {selected_period_label}</div>', unsafe_allow_html=True)
        bins_by_variety = (
            summary_filtered.groupby("variety", as_index=False)["bins_run"].sum()
            .sort_values("bins_run", ascending=False))
        if not bins_by_variety.empty:
            total_p = bins_by_variety["bins_run"].sum()
            bins_by_variety["share"] = (bins_by_variety["bins_run"] / total_p * 100).round(1)
            fig_pie = px.pie(bins_by_variety, names="variety", values="bins_run",
                             hole=0.55, color_discrete_sequence=COLOR_SEQ)
            fig_pie.update_traces(textposition="outside", textfont_size=10,
                                  hovertemplate="%{label}<br>%{value:,.0f} bins (%{percent})")
            apply_plot_theme(fig_pie, height=340)
            fig_pie.update_layout(showlegend=True, legend=dict(orientation="v", x=1, y=0.5))
            st.plotly_chart(fig_pie, use_container_width=True)

    # ── Top contributors ────────────────────────────────────
    st.markdown('<div class="section-title">Top Contributors</div>', unsafe_allow_html=True)
    tc1, tc2, tc3, tc4 = st.columns(4)

    grower_bins = summary_filtered.groupby("grower", as_index=False)["bins_run"].sum().sort_values("bins_run", ascending=False)
    top_variety = bins_by_variety.iloc[0]["variety"] if not bins_by_variety.empty else "N/A"
    top_grower  = grower_bins.iloc[0]["grower"] if not grower_bins.empty else "N/A"

    retip_focus_grower = "N/A"
    if "retip" in summary_filtered.columns:
        rg = summary_filtered.groupby("grower", as_index=False)["retip"].sum().sort_values("retip", ascending=False)
        if not rg.empty: retip_focus_grower = rg.iloc[0]["grower"]

    top_dt_area = "N/A"
    if not downtime_filtered.empty and "downtime_area" in downtime_filtered.columns:
        ac = downtime_filtered["downtime_area"].dropna().astype(str).value_counts()
        if not ac.empty: top_dt_area = ac.index[0]

    tc1.markdown(kpi_html("Top Variety", top_variety), unsafe_allow_html=True)
    tc2.markdown(kpi_html("Top Grower", top_grower), unsafe_allow_html=True)
    tc3.markdown(kpi_html("Most Retipped Grower", retip_focus_grower), unsafe_allow_html=True)
    tc4.markdown(kpi_html("Top Downtime Area", top_dt_area), unsafe_allow_html=True)

    st.markdown("---")

    # ── NEW: Bins/Hour by Grower bar chart ──────────────────
    if "bins_per_hour_row" in summary_filtered.columns:
        st.markdown('<div class="section-title">Throughput Efficiency by Grower</div>', unsafe_allow_html=True)
        bph_grower = (
            summary_filtered.groupby("grower", as_index=False)
            .apply(lambda g: pd.Series({
                "bins_per_hour": g["total_bins_with_retip"].sum() / g["run_hours"].sum()
                    if g["run_hours"].sum() > 0 else None,
                "total_bins": g["bins_run"].sum()
            }))
            .dropna(subset=["bins_per_hour"])
            .sort_values("bins_per_hour", ascending=True)
        )
        if not bph_grower.empty:
            overall_bph = cur_bph
            fig_bph = px.bar(bph_grower, x="bins_per_hour", y="grower", orientation="h",
                             color="bins_per_hour", color_continuous_scale=["#1e2435", AMBER],
                             labels={"bins_per_hour": "Bins/hr", "grower": "Grower"})
            if overall_bph:
                fig_bph.add_vline(x=overall_bph, line_dash="dot", line_color=ROSE,
                                  annotation_text=f"Avg {overall_bph:.1f}", annotation_font_color=ROSE)
            fig_bph.update_coloraxes(showscale=False)
            fig_bph.update_traces(hovertemplate="%{x:.1f} bins/hr")
            apply_plot_theme(fig_bph, height=max(280, len(bph_grower)*32))
            st.plotly_chart(fig_bph, use_container_width=True)

    st.markdown("---")

    # ── Variety deep-dive ───────────────────────────────────
    st.markdown('<div class="section-title">Variety Deep-Dive</div>', unsafe_allow_html=True)
    available_varieties = sorted(summary_filtered["variety"].dropna().astype(str).unique().tolist())
    sv1, sv2 = st.columns([1, 4])
    with sv1:
        selected_summary_variety = st.selectbox("Select Variety", available_varieties or ["N/A"], key="sum_var")
    variety_filtered = summary_filtered[summary_filtered["variety"].astype(str) == selected_summary_variety].copy()

    vbph = None
    if "total_bins_with_retip" in variety_filtered.columns and "run_hours" in variety_filtered.columns:
        vth = variety_filtered["run_hours"].sum()
        vtb = variety_filtered["total_bins_with_retip"].sum()
        if pd.notna(vth) and vth > 0: vbph = vtb / vth

    total_retip_v = variety_filtered["retip"].sum() if "retip" in variety_filtered.columns else None
    total_bins_v  = variety_filtered["bins_run"].sum() if "bins_run" in variety_filtered.columns else None
    run_days_v    = variety_filtered["run_date"].nunique() if "run_date" in variety_filtered.columns else None

    vk1, vk2, vk3, vk4 = st.columns(4)
    vk1.markdown(kpi_html("Bins Run", f"{int(total_bins_v):,}" if total_bins_v else "N/A"), unsafe_allow_html=True)
    vk2.markdown(kpi_html("Bins / Hour", f"{vbph:.1f}" if vbph else "N/A"), unsafe_allow_html=True)
    vk3.markdown(kpi_html("Retip", f"{int(total_retip_v):,}" if total_retip_v else "N/A"), unsafe_allow_html=True)
    vk4.markdown(kpi_html("Active Run Days", str(run_days_v) if run_days_v else "N/A"), unsafe_allow_html=True)

    # Bins by grower for this variety
    bins_by_grower_v = (
        variety_filtered.groupby("grower", as_index=False)
        .agg(total_bins=("bins_run","sum"), period_start=("run_date","min"), period_end=("run_date","max"))
        .sort_values("total_bins", ascending=True))

    vl, vr = st.columns([1.6, 1.4])
    with vl:
        if not bins_by_grower_v.empty:
            fig_vg = px.bar(bins_by_grower_v, x="total_bins", y="grower", orientation="h",
                            color_discrete_sequence=[BLUE],
                            labels={"total_bins": "Total Bins", "grower": "Grower"})
            fig_vg.update_traces(hovertemplate="%{x:,.0f} bins")
            apply_plot_theme(fig_vg, height=max(240, len(bins_by_grower_v)*36))
            st.plotly_chart(fig_vg, use_container_width=True)
    with vr:
        if not bins_by_grower_v.empty:
            disp = bins_by_grower_v.rename(columns={"grower":"Grower","total_bins":"Bins"})[["Grower","Bins"]].sort_values("Bins", ascending=False)
            disp["Bins"] = disp["Bins"].map(lambda x: f"{int(x):,}")
            st.dataframe(disp, use_container_width=True, height=280)

    # ── Downtime section ────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-title">Downtime Analysis</div>', unsafe_allow_html=True)

    dl, dm, dr2 = st.columns([1, 1.5, 1.5])

    with dl:
        total_dt = downtime_filtered["duration_hours"].sum() if "duration_hours" in downtime_filtered.columns else None
        st.markdown(kpi_html("Total Downtime (hrs)", f"{total_dt:.2f}" if total_dt else "N/A"), unsafe_allow_html=True)

        # NEW: downtime % of run hours
        if total_dt and total_hours and total_hours > 0:
            dt_pct = (total_dt / (total_hours + total_dt)) * 100
            st.markdown(kpi_html("Downtime %", f"{dt_pct:.1f}%", "of total scheduled hours", "neu"), unsafe_allow_html=True)

    with dm:
        # Area breakdown chart
        if not downtime_filtered.empty and "downtime_area" in downtime_filtered.columns:
            area_hrs = (downtime_filtered.groupby("downtime_area", as_index=False)["duration_hours"]
                        .sum().sort_values("duration_hours", ascending=False))
            if not area_hrs.empty:
                fig_dt = px.bar(area_hrs, x="downtime_area", y="duration_hours",
                                color_discrete_sequence=[ROSE],
                                labels={"downtime_area": "Area", "duration_hours": "Hours"})
                fig_dt.update_traces(hovertemplate="%{y:.2f} hrs")
                apply_plot_theme(fig_dt, height=260)
                st.plotly_chart(fig_dt, use_container_width=True)

    with dr2:
        if not downtime_filtered.empty:
            dt_tbl = downtime_filtered.copy()
            cols_show = [c for c in ["duration_hours","downtime_area","downtime_reason"] if c in dt_tbl.columns]
            dt_tbl = dt_tbl[cols_show].rename(columns={
                "duration_hours":"Hours","downtime_area":"Area","downtime_reason":"Reason"
            }).sort_values("Hours", ascending=False)
            dt_tbl["Hours"] = dt_tbl["Hours"].map(lambda x: f"{x:.2f}")
            st.dataframe(dt_tbl, use_container_width=True, height=280)
        else:
            st.info("No downtime recorded for this period.")

# ═══════════════════════════════════════════════════════════════
# QUALITY TAB
# ═══════════════════════════════════════════════════════════════
with tab_quality:
    quality_runs = runs.copy()
    quality_runs["month_label"] = quality_runs["run_date"].dt.to_period("M").astype(str)

    # ── Filters ─────────────────────────────────────────────
    qf1, qf2, qf3 = st.columns(3)
    with qf1:
        selected_variety = st.selectbox("Variety", ["All"] + sorted(quality_runs["variety"].dropna().astype(str).unique()), key="q_var")
    with qf2:
        selected_grower = st.selectbox("Grower", ["All"] + sorted(quality_runs["grower"].dropna().astype(str).unique()), key="q_grower")
    with qf3:
        selected_quality_month = st.selectbox("Month", ["All"] + sorted(quality_runs["month_label"].dropna().astype(str).unique(), reverse=True), key="q_month")

    quality_filtered = quality_runs.copy()
    if selected_variety != "All": quality_filtered = quality_filtered[quality_filtered["variety"].astype(str) == selected_variety]
    if selected_grower != "All":  quality_filtered = quality_filtered[quality_filtered["grower"].astype(str) == selected_grower]
    if selected_quality_month != "All": quality_filtered = quality_filtered[quality_filtered["month_label"].astype(str) == selected_quality_month]

    # ── Quality rate KPIs ───────────────────────────────────
    rate_cols = [c for c in ["premium_rate","c1_color_rate","c1_quality_rate","c2_color_rate","c2_quality_rate","no_color_rate","juice_rate"] if c in quality_filtered.columns]
    label_map = {
        "premium_rate":"Premium","c1_color_rate":"C1 Color","c1_quality_rate":"C1 Quality",
        "c2_color_rate":"C2 Color","c2_quality_rate":"C2 Quality","no_color_rate":"No Color","juice_rate":"Juice"
    }

    if rate_cols:
        avgs = quality_filtered[rate_cols].mean()
        st.markdown('<div class="section-title">Average Quality Rates (%)</div>', unsafe_allow_html=True)

        rate_kpi_cols = st.columns(len(rate_cols))
        for i, col in enumerate(rate_cols):
            val = avgs[col]
            # colour logic: premium is good (green), juice/no_color is loss (red)
            if col == "premium_rate":
                direction = "up"
            elif col in ["juice_rate","no_color_rate"]:
                direction = "down"
            else:
                direction = "neu"
            rate_kpi_cols[i].markdown(
                kpi_html(label_map.get(col, col), f"{val:.1f}%" if pd.notna(val) else "N/A", "", direction),
                unsafe_allow_html=True)

    st.markdown("---")

    # ── Chart: Grade distribution ────────────────────────────
    cl1, cl2 = st.columns([1.5, 1])

    with cl1:
        st.markdown('<div class="section-title">Grade Distribution Over Time</div>', unsafe_allow_html=True)
        if rate_cols and not quality_filtered.empty:
            trend_df = quality_filtered.copy()
            trend_df["period"] = trend_df["run_date"].dt.to_period("M").astype(str)
            trend_grp = trend_df.groupby("period")[rate_cols].mean().reset_index()
            fig_trend = go.Figure()
            for col, color in zip(rate_cols, COLOR_SEQ):
                fig_trend.add_trace(go.Scatter(
                    x=trend_grp["period"], y=trend_grp[col],
                    name=label_map.get(col, col),
                    mode="lines+markers", line=dict(color=color, width=2),
                    hovertemplate=f"{label_map.get(col, col)}: %{{y:.1f}}%"
                ))
            apply_plot_theme(fig_trend, height=360)
            st.plotly_chart(fig_trend, use_container_width=True)

    with cl2:
        st.markdown('<div class="section-title">Run Details</div>', unsafe_allow_html=True)
        preview_cols = [c for c in ["run_date","run_id","grower","variety","bins_run","premium_rate","juice_rate","test_drop_count"] if c in quality_filtered.columns]
        st.dataframe(quality_filtered[preview_cols].head(20), use_container_width=True, height=380)

    st.markdown("---")

    # ── Premium vs Loss insight ──────────────────────────────
    st.markdown('<div class="section-title">Loss Analysis</div>', unsafe_allow_html=True)

    il1, il2 = st.columns([1.2, 1.8])

    with il1:
        # NEW: stacked insight — premium vs total loss
        if "premium_rate" in avgs and "juice_rate" in avgs:
            premium_v = avgs.get("premium_rate", 0)
            juice_v   = avgs.get("juice_rate", 0)
            c1c       = avgs.get("c1_color_rate", 0)
            c1q       = avgs.get("c1_quality_rate", 0)
            noc       = avgs.get("no_color_rate", 0)
            total_loss = juice_v + noc

            if pd.notna(premium_v) and premium_v > 0:
                st.markdown(f'<div class="good-card">✔ Premium avg: <b>{premium_v:.1f}%</b></div>', unsafe_allow_html=True)
            if pd.notna(total_loss) and total_loss > 0:
                st.markdown(f'<div class="alert-card">⚠ Juice + No-Color loss: <b>{total_loss:.1f}%</b></div>', unsafe_allow_html=True)
            if pd.notna(c1c) and pd.notna(c1q):
                if c1c > c1q:
                    st.markdown(f'<div class="alert-card">⚠ Color loss ({c1c:.1f}%) exceeds quality loss ({c1q:.1f}%)</div>', unsafe_allow_html=True)
                elif c1q > c1c:
                    st.markdown(f'<div class="alert-card">⚠ Quality loss ({c1q:.1f}%) exceeds color loss ({c1c:.1f}%)</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="good-card">Color & quality loss balanced ({c1c:.1f}%)</div>', unsafe_allow_html=True)

            # NEW: test drop insight
            if "test_drop_count" in quality_filtered.columns:
                avg_td = quality_filtered["test_drop_count"].mean()
                if pd.notna(avg_td):
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Avg Test Drops / Run</div><div class="kpi-value">{avg_td:.1f}</div></div>', unsafe_allow_html=True)

    with il2:
        # Grade breakdown radar / bar
        if rate_cols:
            radar_vals = [avgs[c] for c in rate_cols if pd.notna(avgs[c])]
            radar_labels = [label_map.get(c, c) for c in rate_cols if pd.notna(avgs[c])]
            if radar_vals:
                fig_rad = go.Figure(go.Bar(
                    x=radar_labels, y=radar_vals,
                    marker_color=[EMERALD if c == "premium_rate" else ROSE if c in ["juice_rate","no_color_rate"] else AMBER for c in rate_cols if pd.notna(avgs[c])],
                    hovertemplate="%{x}: %{y:.1f}%"
                ))
                apply_plot_theme(fig_rad, height=280)
                fig_rad.update_layout(showlegend=False, yaxis_title="Avg Rate %")
                st.plotly_chart(fig_rad, use_container_width=True)

    st.markdown("---")

    # ── Defects + Modes ─────────────────────────────────────
    st.markdown('<div class="section-title">Defects & Mode Activity</div>', unsafe_allow_html=True)

    top_defects = pd.DataFrame(columns=["defect","count"])
    top_adjusted = pd.DataFrame(columns=["mode","count"])
    top_checked  = pd.DataFrame(columns=["mode","count"])

    if batches is not None:
        batch_filtered = batches.copy()
        if selected_variety != "All" and "variety" in batch_filtered.columns:
            batch_filtered = batch_filtered[batch_filtered["variety"].astype(str) == selected_variety]
        if selected_grower != "All" and "grower" in batch_filtered.columns:
            batch_filtered = batch_filtered[batch_filtered["grower"].astype(str) == selected_grower]
        defect_cols = [c for c in ["defect_1","defect_2","defect_3"] if c in batch_filtered.columns]
        if defect_cols:
            dv = batch_filtered[defect_cols].melt(value_name="defect")["defect"].dropna().astype(str).str.strip()
            dv = dv[dv != ""]
            if not dv.empty:
                top_defects = dv.value_counts().reset_index()
                top_defects.columns = ["defect","count"]

    if changes is not None:
        ch = changes.copy()
        if selected_variety != "All" and "variety" in ch.columns:
            ch = ch[ch["variety"].astype(str) == selected_variety]
        run_ids = quality_filtered["run_id"].dropna().astype(str).unique().tolist()
        if "run_id" in ch.columns:
            ch = ch[ch["run_id"].astype(str).isin(run_ids)]
        if "mode" in ch.columns and "action" in ch.columns:
            adjusted = ch[ch["action"].astype(str).str.lower().str.startswith("a")]
            checked  = ch[ch["action"].astype(str).str.lower().str.startswith("c")]
            if not adjusted.empty:
                top_adjusted = adjusted["mode"].astype(str).value_counts().reset_index()
                top_adjusted.columns = ["mode","count"]
            if not checked.empty:
                top_checked = checked["mode"].astype(str).value_counts().reset_index()
                top_checked.columns = ["mode","count"]

    dm1, dm2, dm3 = st.columns(3)

    with dm1:
        st.markdown('<div class="section-title">Top Defects</div>', unsafe_allow_html=True)
        if not top_defects.empty:
            fig_def = px.bar(top_defects.head(8), x="count", y="defect", orientation="h",
                             color_discrete_sequence=[ROSE])
            fig_def.update_traces(hovertemplate="%{y}: %{x}")
            apply_plot_theme(fig_def, height=280)
            st.plotly_chart(fig_def, use_container_width=True)
        else:
            st.info("No defect data.")

    with dm2:
        st.markdown('<div class="section-title">Top Adjusted Modes</div>', unsafe_allow_html=True)
        if not top_adjusted.empty:
            fig_adj = px.bar(top_adjusted.head(8), x="count", y="mode", orientation="h",
                             color_discrete_sequence=[AMBER])
            apply_plot_theme(fig_adj, height=280)
            st.plotly_chart(fig_adj, use_container_width=True)
        else:
            st.info("No adjustment data.")

    with dm3:
        st.markdown('<div class="section-title">Top Checked Modes</div>', unsafe_allow_html=True)
        if not top_checked.empty:
            fig_chk = px.bar(top_checked.head(8), x="count", y="mode", orientation="h",
                             color_discrete_sequence=[BLUE])
            apply_plot_theme(fig_chk, height=280)
            st.plotly_chart(fig_chk, use_container_width=True)
        else:
            st.info("No check data.")

    # ── NEW: Premium trend by variety ───────────────────────
    if "premium_rate" in quality_runs.columns and "variety" in quality_runs.columns:
        st.markdown("---")
        st.markdown('<div class="section-title">Premium Rate by Variety (All Time)</div>', unsafe_allow_html=True)
        prem_variety = (
            quality_runs.groupby("variety", as_index=False)["premium_rate"].mean()
            .dropna().sort_values("premium_rate", ascending=False))
        if not prem_variety.empty:
            fig_pv = px.bar(prem_variety, x="variety", y="premium_rate",
                            color="premium_rate", color_continuous_scale=["#1e2435", EMERALD],
                            labels={"variety": "Variety", "premium_rate": "Avg Premium %"})
            fig_pv.update_coloraxes(showscale=False)
            fig_pv.update_traces(hovertemplate="%{x}: %{y:.1f}%")
            apply_plot_theme(fig_pv, height=280)
            st.plotly_chart(fig_pv, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# MODE TAB
# ═══════════════════════════════════════════════════════════════
with tab_mode:
    if changes is None:
        st.info("changes_raw.csv not found.")
    else:
        mode_df = changes.copy()

        if "run_id" in mode_df.columns and "run_id" in runs.columns:
            mode_df = mode_df.merge(
                runs[["run_id","batch_id","grower","variety","run_date"]], on="run_id", how="left", suffixes=("","_run"))

        if batches is not None and "batch_id" in mode_df.columns and "batch_id" in batches.columns:
            bcols = [c for c in ["batch_id","grower","variety","decfile_version","defect_1","defect_2","defect_3"] if c in batches.columns]
            mode_df = mode_df.merge(batches[bcols], on="batch_id", how="left", suffixes=("","_batch"))

        for col in ["grower","variety","decfile_version","mode","check_class","reason","action","sensitivity","accuracy"]:
            if col in mode_df.columns:
                mode_df[col] = mode_df[col].fillna("").astype(str).str.strip().replace("", pd.NA)

        if "boundary_before" in mode_df.columns: mode_df["boundary_before"] = pd.to_numeric(mode_df["boundary_before"], errors="coerce")
        if "boundary_after"  in mode_df.columns: mode_df["boundary_after"]  = pd.to_numeric(mode_df["boundary_after"],  errors="coerce")

        # ── Filters ─────────────────────────────────────────
        mf1, mf2, mf3 = st.columns(3)
        with mf1:
            av = ["All"] + sorted(mode_df["variety"].dropna().astype(str).unique()) if "variety" in mode_df.columns else ["All"]
            selected_mode_variety = st.selectbox("Variety", av, key="m_var")
        filtered_mode = mode_df.copy()
        if selected_mode_variety != "All" and "variety" in filtered_mode.columns:
            filtered_mode = filtered_mode[filtered_mode["variety"].astype(str) == selected_mode_variety]

        with mf2:
            ag = ["All"] + sorted(filtered_mode["grower"].dropna().astype(str).unique()) if "grower" in filtered_mode.columns else ["All"]
            selected_mode_grower = st.selectbox("Grower", ag, key="m_grower")
        if selected_mode_grower != "All" and "grower" in filtered_mode.columns:
            filtered_mode = filtered_mode[filtered_mode["grower"].astype(str) == selected_mode_grower]

        with mf3:
            aver = ["All"] + sorted(filtered_mode["decfile_version"].dropna().astype(str).unique()) if "decfile_version" in filtered_mode.columns else ["All"]
            selected_version = st.selectbox("Version", aver, key="m_ver")
        if selected_version != "All" and "decfile_version" in filtered_mode.columns:
            filtered_mode = filtered_mode[filtered_mode["decfile_version"].astype(str) == selected_version]

        # ── Overview KPIs ────────────────────────────────────
        total_changes = len(filtered_mode)
        adj_count = chk_count = 0
        if "action" in filtered_mode.columns:
            adj_count = filtered_mode["action"].astype(str).str.lower().str.startswith("a").sum()
            chk_count = filtered_mode["action"].astype(str).str.lower().str.startswith("c").sum()
        unique_modes = filtered_mode["mode"].dropna().nunique() if "mode" in filtered_mode.columns else 0

        mk1, mk2, mk3, mk4 = st.columns(4)
        mk1.markdown(kpi_html("Total Changes", f"{total_changes:,}"), unsafe_allow_html=True)
        mk2.markdown(kpi_html("Adjustments (A)", f"{adj_count:,}", "boundary changed"), unsafe_allow_html=True)
        mk3.markdown(kpi_html("Checks (C)", f"{chk_count:,}", "boundary verified"), unsafe_allow_html=True)
        mk4.markdown(kpi_html("Unique Modes", f"{unique_modes:,}"), unsafe_allow_html=True)

        st.markdown("---")

        # ── Top defects + boundary change viz ────────────────
        top_left, top_right = st.columns([1, 1])

        with top_left:
            st.markdown('<div class="section-title">Top Defects for Selection</div>', unsafe_allow_html=True)
            batches_mode = None
            if batches is not None:
                bm = batches.copy()
                for col in ["grower","variety","decfile_version","defect_1","defect_2","defect_3"]:
                    if col in bm.columns:
                        bm[col] = bm[col].fillna("").astype(str).str.strip().replace("", pd.NA)
                batches_mode = bm

            top_defects_mode = pd.DataFrame(columns=["Defect","Count"])
            if batches_mode is not None:
                fbm = batches_mode.copy()
                if selected_mode_variety != "All" and "variety" in fbm.columns:
                    fbm = fbm[fbm["variety"].astype(str) == selected_mode_variety]
                if selected_mode_grower != "All" and "grower" in fbm.columns:
                    fbm = fbm[fbm["grower"].astype(str) == selected_mode_grower]
                dcols = [c for c in ["defect_1","defect_2","defect_3"] if c in fbm.columns]
                if dcols:
                    md = fbm[dcols].melt(value_name="defect")["defect"].dropna().astype(str).str.strip()
                    md = md[md != ""]
                    if not md.empty:
                        top_defects_mode = md.value_counts().reset_index()
                        top_defects_mode.columns = ["Defect","Count"]

            if not top_defects_mode.empty:
                fig_tdm = px.bar(top_defects_mode.head(8), x="Count", y="Defect", orientation="h",
                                 color_discrete_sequence=[ROSE])
                apply_plot_theme(fig_tdm, height=280)
                st.plotly_chart(fig_tdm, use_container_width=True)
            else:
                st.info("No defect data for current filters.")

        with top_right:
            st.markdown('<div class="section-title">Boundary Change Distribution</div>', unsafe_allow_html=True)
            # NEW: show histogram of boundary changes (after - before)
            if "boundary_before" in filtered_mode.columns and "boundary_after" in filtered_mode.columns:
                filtered_mode["boundary_delta"] = filtered_mode["boundary_after"] - filtered_mode["boundary_before"]
                deltas = filtered_mode["boundary_delta"].dropna()
                if not deltas.empty:
                    fig_delta = px.histogram(deltas, nbins=30,
                                             color_discrete_sequence=[AMBER],
                                             labels={"value":"Boundary Change", "count":"Count"})
                    fig_delta.add_vline(x=0, line_dash="dot", line_color=ROSE)
                    apply_plot_theme(fig_delta, height=280)
                    fig_delta.update_layout(showlegend=False, xaxis_title="Boundary After − Before", yaxis_title="Count")
                    st.plotly_chart(fig_delta, use_container_width=True)
            else:
                st.info("Boundary data not available.")

        st.markdown("---")

        # ── Top adjusted modes table ──────────────────────────
        st.markdown('<div class="section-title">Top Adjusted Modes</div>', unsafe_allow_html=True)

        adjusted_mode_table = pd.DataFrame()
        if "mode" in filtered_mode.columns and "action" in filtered_mode.columns:
            adjusted = filtered_mode[filtered_mode["action"].astype(str).str.lower().str.startswith("a")].copy()
            if not adjusted.empty:
                rows = []
                gcols = ["mode"] + (["check_class"] if "check_class" in adjusted.columns else [])
                for keys, grp in adjusted.groupby(gcols, dropna=False):
                    mode_name  = keys[0] if isinstance(keys, tuple) else keys
                    check_class = keys[1] if isinstance(keys, tuple) and len(keys) > 1 else ""
                    _, allb = summarize_boundaries(grp["boundary_after"]) if "boundary_after" in grp.columns else ("","")
                    sensitivity_text = ", ".join(sorted(set(grp["sensitivity"].dropna().astype(str)))) if "sensitivity" in grp.columns else ""
                    accuracy_text    = ", ".join(sorted(set(grp["accuracy"].dropna().astype(str)))) if "accuracy" in grp.columns else ""
                    rows.append({"Check": False, "Mode": mode_name, "Check Class": check_class,
                                 "Count": len(grp), "Reference Boundaries": allb,
                                 "Sensitivity": sensitivity_text, "Accuracy": accuracy_text})
                adjusted_mode_table = pd.DataFrame(rows).sort_values(["Count","Mode"], ascending=[False, True]).reset_index(drop=True)

        if not adjusted_mode_table.empty:
            st.data_editor(adjusted_mode_table, use_container_width=True, height=300, hide_index=True,
                column_config={"Check": st.column_config.CheckboxColumn("Check")},
                disabled=["Mode","Check Class","Count","Reference Boundaries","Sensitivity","Accuracy"])
        else:
            st.info("No adjusted mode data.")

        st.markdown("---")

        # ── Defect investigation ──────────────────────────────
        st.markdown('<div class="section-title">Defect Investigation Workflow</div>', unsafe_allow_html=True)

        step1, step2 = st.columns(2)

        with step1:
            st.markdown("**Step 1 — Select defect to investigate**")
            available_reason_items = []
            if "reason" in filtered_mode.columns:
                sr = filtered_mode["reason"].dropna().astype(str).str.split(",").explode().astype(str).str.strip()
                available_reason_items = sorted(sr[sr != ""].unique().tolist())

            selected_reason = st.selectbox("Defect / Reason", ["All"] + available_reason_items, key="m_reason")

            related_modes = pd.DataFrame()
            if selected_reason != "All":
                rdf = filtered_mode.copy()
                rdf["reason_item"] = rdf["reason"].fillna("").astype(str).str.split(",")
                rdf = rdf.explode("reason_item")
                rdf["reason_item"] = rdf["reason_item"].astype(str).str.strip()
                rdf = rdf[rdf["reason_item"] == selected_reason].copy()

                if not rdf.empty:
                    rows = []
                    for keys, grp in rdf.groupby(["mode","check_class"], dropna=False):
                        _, allb = summarize_boundaries(grp["boundary_after"]) if "boundary_after" in grp.columns else ("","")
                        rows.append({"Mode": keys[0], "Check Class": keys[1], "Count": len(grp),
                                     "Reference Boundaries": allb})
                    related_modes = pd.DataFrame(rows).sort_values("Count", ascending=False)

            if not related_modes.empty:
                st.dataframe(related_modes, use_container_width=True, height=240)
            elif selected_reason != "All":
                st.info("No related modes found.")

        with step2:
            st.markdown("**Step 2 — What else can this mode detect?**")
            mode_options = related_modes["Mode"].dropna().astype(str).unique().tolist() if not related_modes.empty else []
            selected_related_mode = st.selectbox("Select mode", ["All"] + sorted(mode_options), key="m_rel_mode")

            if selected_related_mode != "All":
                sel_mode_rows = filtered_mode[filtered_mode["mode"].astype(str) == selected_related_mode].copy()
                if "reason" in sel_mode_rows.columns:
                    other_reasons = (sel_mode_rows["reason"].dropna().astype(str).str.split(",")
                                     .explode().astype(str).str.strip())
                    other_reasons = other_reasons[other_reasons != ""]
                    if not other_reasons.empty:
                        orc = other_reasons.value_counts().reset_index()
                        orc.columns = ["Recorded Reason","Count"]
                        st.dataframe(orc, use_container_width=True, height=240)
                    else:
                        st.info("No other recorded reasons.")
            else:
                st.info("Select a mode above.")

        # Step 3 — unchecked modes
        st.markdown("---")
        st.markdown("**Step 3 — Unchecked modes for this grower / variety**")

        next_modes_table = pd.DataFrame()
        if selected_mode_variety != "All" and selected_mode_grower != "All":
            variety_mode_db = mode_df.copy()
            if "variety" in variety_mode_db.columns:
                variety_mode_db = variety_mode_db[variety_mode_db["variety"].astype(str) == selected_mode_variety]
            if selected_version != "All" and "decfile_version" in variety_mode_db.columns:
                variety_mode_db = variety_mode_db[variety_mode_db["decfile_version"].astype(str) == selected_version]

            grower_mode_db = variety_mode_db.copy()
            if "grower" in grower_mode_db.columns:
                grower_mode_db = grower_mode_db[grower_mode_db["grower"].astype(str) == selected_mode_grower]

            checked_pairs = set()
            if not grower_mode_db.empty:
                for keys, _ in grower_mode_db.groupby(["mode","check_class"], dropna=False):
                    checked_pairs.add((str(keys[0]), str(keys[1])))

            rows = []
            for keys, grp in variety_mode_db.groupby(["mode","check_class"], dropna=False):
                mn = str(keys[0]); cc = str(keys[1])
                if (mn, cc) in checked_pairs: continue
                _, allb = summarize_boundaries(grp["boundary_after"]) if "boundary_after" in grp.columns else ("","")
                rows.append({"Check": False, "Mode": mn, "Check Class": cc, "Count": len(grp), "Reference Boundaries": allb})

            if rows:
                next_modes_table = pd.DataFrame(rows).sort_values("Count", ascending=False).reset_index(drop=True)

        if selected_mode_variety == "All" or selected_mode_grower == "All":
            st.info("Select a specific variety and grower to see unchecked modes.")
        elif not next_modes_table.empty:
            st.data_editor(next_modes_table, use_container_width=True, height=280, hide_index=True,
                column_config={"Check": st.column_config.CheckboxColumn("Check")},
                disabled=["Mode","Check Class","Count","Reference Boundaries"])
        else:
            st.info("No additional unchecked modes for this grower.")

# ═══════════════════════════════════════════════════════════════
# OPERATORS TAB  ← NEW
# ═══════════════════════════════════════════════════════════════
with tab_operators:
    st.markdown('<div class="section-title">Operator & Machine Performance</div>', unsafe_allow_html=True)

    ops_df = runs.copy()
    has_machine  = "operator_machine"  in ops_df.columns
    has_quality  = "operator_quality"  in ops_df.columns
    has_bph      = "bins_per_hour_row" in ops_df.columns

    if not has_machine and not has_quality:
        st.info("No operator columns found in runs_raw.csv.")
    else:
        # Filter
        op_f1, op_f2 = st.columns(2)
        with op_f1:
            month_opts = sorted(ops_df["run_date"].dt.to_period("M").astype(str).unique(), reverse=True)
            sel_op_month = st.selectbox("Month", ["All"] + month_opts, key="op_month")
        with op_f2:
            variety_opts = sorted(ops_df["variety"].dropna().astype(str).unique()) if "variety" in ops_df.columns else []
            sel_op_var = st.selectbox("Variety", ["All"] + variety_opts, key="op_var")

        ops_df["month_label"] = ops_df["run_date"].dt.to_period("M").astype(str)
        if sel_op_month != "All": ops_df = ops_df[ops_df["month_label"] == sel_op_month]
        if sel_op_var != "All" and "variety" in ops_df.columns: ops_df = ops_df[ops_df["variety"].astype(str) == sel_op_var]

        ops_cols = st.columns(2)

        if has_machine:
            with ops_cols[0]:
                st.markdown('<div class="section-title">Machine Operator — Throughput</div>', unsafe_allow_html=True)
                mach_grp = ops_df.groupby("operator_machine", as_index=False).apply(
                    lambda g: pd.Series({
                        "bins_run": g["bins_run"].sum(),
                        "bins_per_hour": (g["total_bins_with_retip"].sum() / g["run_hours"].sum()
                                          if "run_hours" in g.columns and g["run_hours"].sum() > 0 else None),
                        "runs": len(g)
                    })
                ).dropna(subset=["operator_machine"])
                mach_grp = mach_grp[mach_grp["operator_machine"].astype(str).str.strip() != ""]

                if not mach_grp.empty:
                    fig_mop = px.bar(mach_grp.sort_values("bins_run", ascending=True),
                                     x="bins_run", y="operator_machine", orientation="h",
                                     color="bins_per_hour", color_continuous_scale=["#1e2435", AMBER],
                                     labels={"bins_run":"Total Bins","operator_machine":"Operator","bins_per_hour":"Bins/hr"},
                                     hover_data={"bins_per_hour":":.1f", "runs":True})
                    fig_mop.update_coloraxes(showscale=False)
                    apply_plot_theme(fig_mop, height=max(280, len(mach_grp)*38))
                    st.plotly_chart(fig_mop, use_container_width=True)
                else:
                    st.info("No machine operator data.")

        if has_quality:
            with ops_cols[1 if has_machine else 0]:
                st.markdown('<div class="section-title">Quality Operator — Average Premium Rate</div>', unsafe_allow_html=True)
                qual_grp = ops_df.groupby("operator_quality", as_index=False).apply(
                    lambda g: pd.Series({
                        "avg_premium": g["premium_rate"].mean() if "premium_rate" in g.columns else None,
                        "avg_juice": g["juice_rate"].mean() if "juice_rate" in g.columns else None,
                        "runs": len(g)
                    })
                ).dropna(subset=["operator_quality"])
                qual_grp = qual_grp[qual_grp["operator_quality"].astype(str).str.strip() != ""]

                if not qual_grp.empty and "avg_premium" in qual_grp.columns:
                    fig_qop = px.bar(qual_grp.dropna(subset=["avg_premium"]).sort_values("avg_premium", ascending=True),
                                     x="avg_premium", y="operator_quality", orientation="h",
                                     color="avg_premium", color_continuous_scale=["#1e2435", EMERALD],
                                     labels={"avg_premium":"Avg Premium %","operator_quality":"Operator"},
                                     hover_data={"avg_juice":":.1f","runs":True})
                    fig_qop.update_coloraxes(showscale=False)
                    apply_plot_theme(fig_qop, height=max(280, len(qual_grp)*38))
                    st.plotly_chart(fig_qop, use_container_width=True)
                else:
                    st.info("No quality operator data or premium rate not recorded.")

        # Speed lanes
        if speed_cols:
            st.markdown("---")
            st.markdown('<div class="section-title">Lane Speed Distribution</div>', unsafe_allow_html=True)
            speed_df = ops_df[speed_cols].melt(var_name="Lane", value_name="Speed").dropna()
            speed_df["Lane"] = speed_df["Lane"].map({
                "Speed_12":"Lanes 1-2","Speed_34":"Lanes 3-4","Speed_56":"Lanes 5-6","full_speed":"Full Speed"
            })
            if not speed_df.empty:
                fig_spd = px.box(speed_df, x="Lane", y="Speed", color="Lane",
                                 color_discrete_sequence=COLOR_SEQ,
                                 labels={"Speed":"Speed","Lane":"Lane Group"})
                apply_plot_theme(fig_spd, height=300)
                fig_spd.update_layout(showlegend=False)
                st.plotly_chart(fig_spd, use_container_width=True)

        # Retip per operator (machine)
        if has_machine and "retip" in ops_df.columns:
            st.markdown("---")
            st.markdown('<div class="section-title">Retip Volume by Machine Operator</div>', unsafe_allow_html=True)
            retip_op = ops_df.groupby("operator_machine", as_index=False)["retip"].sum()
            retip_op = retip_op[retip_op["operator_machine"].astype(str).str.strip() != ""].sort_values("retip", ascending=False)
            if not retip_op.empty:
                fig_ret = px.bar(retip_op, x="operator_machine", y="retip",
                                 color_discrete_sequence=[ROSE],
                                 labels={"operator_machine":"Operator","retip":"Total Retip"})
                apply_plot_theme(fig_ret, height=260)
                st.plotly_chart(fig_ret, use_container_width=True)
