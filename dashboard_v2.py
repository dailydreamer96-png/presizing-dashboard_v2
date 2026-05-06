import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG — Streamlit's sidebar is permanently hidden;
# we use our own collapsible top-bar inside the main content
# (Streamlit cannot reliably toggle its sidebar from Python).
# ─────────────────────────────────────────────────────────────
if "show_filters" not in st.session_state:
    st.session_state.show_filters = True

st.set_page_config(
    page_title="Presizing · Operations Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# DESIGN SYSTEM — Dodger Blue · Soft slate-blue background
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Inter:wght@400;500;600;700;800&display=swap');

  :root {
    /* Brand */
    --blue:       #1E90FF;   /* Dodger Blue */
    --blue-dk:    #1270cc;   /* pressed / darker */
    --blue-lt:    #dbeeff;   /* tint bg */
    --blue-md:    #93c5fd;   /* mid tint for borders */

    /* Background layers — soft blue-grey slate */
    --bg:         #e8edf5;   /* page canvas */
    --surface:    #f4f7fb;   /* card face */
    --surface2:   #edf1f8;   /* input fill / alt rows */
    --sidebar-bg: #1a2744;   /* sidebar dark navy */

    /* Borders */
    --border:     #d0d8e8;
    --border-strong: #b8c4d8;

    /* Status */
    --emerald:    #059669;
    --emerald-lt: #d1fae5;
    --rose:       #dc2626;
    --rose-lt:    #fee2e2;

    /* Text — dark enough to pop on light bg */
    --ink:        #0f1d35;   /* headings */
    --ink-mid:    #2d3f5e;   /* body */
    --ink-soft:   #4e6080;   /* secondary */
    --ink-faint:  #7a90b0;   /* hints / labels */
  }

  /* ── Global ─────────────────────────────────────── */
  html, body,
  [data-testid="stAppViewContainer"],
  [data-testid="stMain"] {
    background: var(--bg) !important;
    color: var(--ink) !important;
    font-family: 'Inter', sans-serif !important;
  }
  [data-testid="stAppViewContainer"] > section > div:first-child { padding-top: 1.5rem !important; }
  [data-testid="stHeader"]  { background: transparent !important; box-shadow: none !important; }

  /* Hide Streamlit's developer toolbar AND main hamburger menu (3-dot kebab).
     This menu is for "Rerun / Settings / Print / Record" and is irrelevant to operators.
     Hiding it also frees up the top-left corner for our custom MENU button. */
  [data-testid="stToolbarActions"],
  [data-testid="stToolbar"],
  [data-testid="stMainMenu"],
  #MainMenu,
  .stAppDeployButton,
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"] {
    display: none !important;
    visibility: hidden !important;
  }

  /* ── Streamlit's built-in sidebar entirely hidden ──
     We replace it with our own collapsible nav-panel in the main content. */
  [data-testid="stSidebar"],
  [data-testid="stSidebarContent"],
  [data-testid="stSidebarCollapseButton"],
  [data-testid="stSidebarCollapsedControl"],
  [data-testid="collapsedControl"],
  button[kind="header"][data-testid="baseButton-header"],
  button[kind="headerNoPadding"],
  [data-testid="stSidebarHeader"] button {
    display: none !important;
    width: 0 !important;
    min-width: 0 !important;
  }

  /* ── Our own nav panel — a dark navy bar in the main content ─ */
  .nav-panel {
    background: var(--sidebar-bg);
    color: #ffffff;
    border-radius: 12px;
    padding: 18px 24px;
    margin-bottom: 18px;
    box-shadow: 0 4px 14px rgba(15, 29, 53, 0.12);
  }
  .nav-panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 0;
  }
  .nav-panel-title {
    color: #ffffff;
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  /* Style any buttons inside the nav panel area (toggle button) */
  .nav-toggle-btn-row [data-testid="stButton"] button {
    background: var(--blue) !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    padding: 10px 22px !important;
    border-radius: 10px !important;
    border: 2px solid #ffffff !important;
    box-shadow: 0 3px 12px rgba(30,144,255,0.4) !important;
    transition: all 0.15s ease !important;
    width: 100%;
  }
  .nav-toggle-btn-row [data-testid="stButton"] button:hover {
    background: var(--blue-dk) !important;
    transform: translateY(-1px) !important;
  }
  .nav-toggle-btn-row [data-testid="stButton"] button p {
    color: #ffffff !important;
    font-weight: 700 !important;
  }

  /* Filters area — light card on the page below the dark nav bar */
  .filters-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 18px;
    box-shadow: 0 1px 4px rgba(15, 29, 53, 0.04);
  }
  .filters-card-title {
    color: var(--ink);
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--blue);
    display: inline-block;
  }

  /* ── Sidebar ─────────────────────────────────────── */
  [data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: none !important;
  }
  [data-testid="stSidebar"] * { color: #c8d8f0 !important; }
  [data-testid="stSidebar"] h2,
  [data-testid="stSidebar"] h3 { color: #ffffff !important; font-size: 0.85rem !important; font-weight: 700 !important; letter-spacing: 0.06em !important; text-transform: uppercase !important; }
  [data-testid="stSidebar"] hr { border-color: #2e4070 !important; }

  /* (Native sidebar close button hidden — replaced by our st.button in Python) */

  /* Sidebar selectbox */
  [data-testid="stSidebar"] [data-testid="stSelectbox"] label {
    color: #7a9fc8 !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
  }
  [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: #1e2f55 !important;
    border: 1px solid #2e4070 !important;
    border-radius: 8px !important;
    color: #e0eaf8 !important;
    font-size: 0.85rem !important;
  }

  /* Sidebar radio */
  [data-testid="stSidebar"] [data-testid="stRadio"] label { color: #7a9fc8 !important; font-size: 0.68rem !important; font-weight: 600 !important; letter-spacing: 0.06em !important; text-transform: uppercase !important; }
  [data-testid="stSidebar"] [data-testid="stRadio"] > div > label {
    background: #1e2f55 !important;
    border: 1px solid #2e4070 !important;
    border-radius: 8px !important;
    color: #c8d8f0 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 8px 14px !important;
    transition: all 0.15s;
  }
  [data-testid="stSidebar"] [data-testid="stRadio"] > div > label:has(input:checked) {
    background: var(--blue) !important;
    border-color: var(--blue-dk) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
  }


  /* Sidebar section heading */
  .sb-section {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #4e6a98;
    padding: 12px 0 6px 0;
    border-bottom: 1px solid #2e4070;
    margin-bottom: 10px;
  }

  /* ── Main content tabs ───────────────────────────── */
  [data-testid="stTabs"] > div:first-child {
    background: var(--surface) !important;
    border-bottom: 2px solid var(--border) !important;
    border-radius: 10px 10px 0 0 !important;
    padding: 0 16px !important;
    gap: 0 !important;
  }
  [data-testid="stTabs"] button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    color: var(--ink-soft) !important;
    padding: 14px 22px !important;
    border-radius: 0 !important;
    border: none !important;
    background: transparent !important;
    transition: color 0.15s;
  }
  [data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--blue) !important;
    border-bottom: 3px solid var(--blue) !important;
    background: transparent !important;
  }
  [data-testid="stTabs"] button:hover:not([aria-selected="true"]) {
    color: var(--ink-mid) !important;
    background: var(--blue-lt) !important;
  }

  /* ── Main selectboxes (filter row) ──────────────── */
  [data-testid="stSelectbox"] label {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    color: var(--ink) !important;
    margin-bottom: 4px !important;
  }
  [data-testid="stSelectbox"] > div > div {
    background: var(--surface) !important;
    border: 1.5px solid var(--border-strong) !important;
    border-radius: 8px !important;
    color: var(--ink) !important;
    font-size: 0.88rem !important;
    font-family: 'Inter', sans-serif !important;
    min-height: 40px !important;
  }
  [data-testid="stSelectbox"] > div > div:focus-within {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(30,144,255,0.15) !important;
  }

  /* ── DataFrames ─────────────────────────────────── */
  [data-testid="stDataFrame"] {
    background: var(--surface) !important;
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    overflow: hidden;
  }
  [data-testid="stDataFrame"] table { font-family: 'DM Mono', monospace !important; font-size: 0.82rem !important; }
  [data-testid="stDataFrame"] th {
    background: var(--sidebar-bg) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.03em !important;
  }
  [data-testid="stDataFrame"] tr:nth-child(even) td { background: var(--surface2) !important; }
  [data-testid="stDataFrame"] td { color: var(--ink) !important; }

  /* ── Divider ────────────────────────────────────── */
  hr { border-color: var(--border) !important; margin: 1.4rem 0 !important; }

  /* ── Info box ───────────────────────────────────── */
  [data-testid="stInfo"] {
    background: var(--blue-lt) !important;
    border-left: 4px solid var(--blue) !important;
    color: var(--ink) !important;
    border-radius: 6px;
    font-size: 0.88rem !important;
    padding: 12px 16px !important;
  }
  [data-testid="stInfo"] p, [data-testid="stInfo"] div {
    color: var(--ink) !important;
    font-size: 0.88rem !important;
  }

  /* Main content radio buttons (e.g. Mode page direction toggle) */
  [data-testid="stMain"] [data-testid="stRadio"] label {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    color: var(--ink) !important;
  }
  [data-testid="stMain"] [data-testid="stRadio"] > div { gap: 8px !important; flex-wrap: wrap !important; }
  [data-testid="stMain"] [data-testid="stRadio"] > div > label {
    background: var(--surface) !important;
    border: 1.5px solid var(--border-strong) !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    color: var(--ink-mid) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    transition: all 0.15s;
    cursor: pointer;
    text-transform: none !important;
    letter-spacing: 0 !important;
  }
  [data-testid="stMain"] [data-testid="stRadio"] > div > label:has(input:checked) {
    border-color: var(--blue) !important;
    color: var(--blue-dk) !important;
    background: var(--blue-lt) !important;
    font-weight: 700 !important;
  }

  /* ── Force readable text colors based on background ───
     Light backgrounds (cards, page) → DARK text
     Dark backgrounds (header, sidebar) → WHITE text */

  /* Default body text on light page */
  [data-testid="stMain"] p,
  [data-testid="stMain"] li,
  [data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
  [data-testid="stMain"] [data-testid="stMarkdownContainer"] li,
  [data-testid="stMain"] [data-testid="stMarkdownContainer"] strong,
  [data-testid="stMain"] [data-testid="stMarkdownContainer"] em {
    color: var(--ink) !important;
  }
  [data-testid="stMain"] [data-testid="stCaptionContainer"],
  [data-testid="stMain"] .stCaption,
  [data-testid="stMain"] [data-testid="stCaptionContainer"] p {
    color: var(--ink-mid) !important;
    font-size: 0.88rem !important;
    line-height: 1.5 !important;
  }

  /* Headings on the light page area — but NOT inside the dark page-header */
  [data-testid="stMain"] :not(.page-header) > h1,
  [data-testid="stMain"] :not(.page-header) > h2,
  [data-testid="stMain"] :not(.page-header) > h3,
  [data-testid="stMain"] :not(.page-header) > h4 {
    color: var(--ink) !important;
  }
  [data-testid="stMain"] h2 { font-size: 1.5rem !important; font-weight: 700 !important; }
  [data-testid="stMain"] h3 { font-size: 1.2rem !important; font-weight: 700 !important; }
  [data-testid="stMain"] h4 { font-size: 1.05rem !important; font-weight: 700 !important; }

  /* Step 1 / Step 2 markdown bold labels — dark on white */
  [data-testid="stMain"] [data-testid="stMarkdownContainer"] strong {
    color: var(--ink) !important;
    font-weight: 700 !important;
  }

  /* ── Section title ──────────────────── */
  .section-title {
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: var(--ink) !important;
    margin-bottom: 14px !important;
    padding-bottom: 8px !important;
    border-bottom: 3px solid var(--blue) !important;
    display: inline-block !important;
  }

  /* ── KPI cards ──────────────────────────────────── */
  .kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 5px solid var(--blue);
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 10px;
    box-shadow: 0 2px 6px rgba(15,29,53,0.06);
  }
  .kpi-label {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: var(--ink-soft) !important;
    margin-bottom: 7px !important;
  }
  .kpi-value {
    font-family: 'DM Mono', monospace !important;
    font-size: 1.75rem !important;
    font-weight: 500 !important;
    color: var(--ink) !important;
    line-height: 1.2 !important;
  }
  .kpi-delta {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    margin-top: 6px !important;
  }
  .kpi-delta.up   { color: var(--emerald); }
  .kpi-delta.down { color: var(--rose); }
  .kpi-delta.neu  { color: var(--ink-faint); }

  /* ── Alert / good cards ─────────────────────────── */
  .alert-card {
    background: var(--rose-lt);
    border: 1px solid #fca5a5;
    border-left: 4px solid var(--rose);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 0.88rem;
    color: #7f1d1d;
    font-weight: 500;
  }
  .good-card {
    background: var(--emerald-lt);
    border: 1px solid #6ee7b7;
    border-left: 4px solid var(--emerald);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 0.88rem;
    color: #065f46;
    font-weight: 500;
  }

  /* ── Page header ────────────────────────────────── */
  .page-header {
    background: var(--sidebar-bg);
    border-radius: 14px;
    padding: 26px 32px;
    margin-bottom: 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 16px rgba(15,29,53,0.12);
  }
  .page-header-left { display: flex; flex-direction: column; gap: 8px; }
  .page-header h1,
  [data-testid="stMain"] .page-header h1 {
    font-family: 'Inter', sans-serif !important;
    font-size: 2.1rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    margin: 0 !important;
    letter-spacing: -0.03em !important;
    line-height: 1.1 !important;
  }
  .page-header h1 span,
  [data-testid="stMain"] .page-header h1 span {
    color: var(--blue) !important;
  }
  .page-header .subtitle,
  [data-testid="stMain"] .page-header .subtitle {
    font-family: 'Inter', sans-serif !important;
    font-size: 1.05rem !important;
    color: #b8cce8 !important;
    margin: 0 !important;
    font-weight: 400 !important;
  }
  .page-header-right { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }
  .header-badge {
    background: var(--blue) !important;
    color: #ffffff !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    padding: 5px 14px !important;
    border-radius: 20px !important;
    letter-spacing: 0.06em !important;
  }
  .header-meta {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #b8cce8 !important;
  }

  /* ── Insight tag ────────────────────────────────── */
  .insight-tag {
    display: inline-block;
    background: var(--blue-lt);
    border: 1.5px solid var(--blue-md);
    color: var(--blue-dk);
    font-size: 0.78rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    padding: 4px 12px;
    border-radius: 100px;
    margin: 3px 3px 3px 0;
  }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# PLOTLY THEME
# ─────────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#f4f7fb",
    font=dict(family="Inter, sans-serif", color="#4e6080", size=12),
    title_font=dict(family="Inter, sans-serif", color="#0f1d35", size=14),
    xaxis=dict(gridcolor="#d0d8e8", linecolor="#d0d8e8", tickfont=dict(size=11), tickcolor="#7a90b0"),
    yaxis=dict(gridcolor="#d0d8e8", linecolor="#d0d8e8", tickfont=dict(size=11), tickcolor="#7a90b0"),
    margin=dict(l=20, r=20, t=44, b=20),
    hovermode="x unified",
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#2d3f5e")),
)
BLUE     = "#1E90FF"   # Dodger Blue — primary
BLUE_DK  = "#1270cc"
NAVY     = "#1a2744"
EMERALD  = "#059669"
ROSE     = "#dc2626"
AMBER    = "#d97706"
PURPLE   = "#7c3aed"
SLATE    = "#4e6080"

# Brand-led color sequence (Dodger blue first)
COLOR_SEQ = [BLUE, NAVY, EMERALD, AMBER, ROSE, PURPLE, "#0891b2", "#db2777"]

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
runs     = load_csv("runs_raw.csv")
batches  = load_csv("batches_raw.csv")
changes  = load_csv("changes_raw.csv")
downtime = load_csv("downtime_raw.csv")
dec_file = load_csv("dec_file_raw.csv")

if runs is None:
    st.error("runs_raw.csv not found.")
    st.stop()

# ─────────────────────────────────────────────────────────────
# CLEAN DEC_FILE — training records
# ─────────────────────────────────────────────────────────────
def _parse_mixed_date(s):
    """Handle 2024-03-06 / 26/01/2024 / 27.02.2024 etc."""
    if pd.isna(s):
        return pd.NaT
    s = str(s).strip().replace(".", "/")
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return pd.to_datetime(s, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.to_datetime(s, errors="coerce", dayfirst=True)

if dec_file is not None:
    for col in ("date_submit", "date_complete"):
        if col in dec_file.columns:
            dec_file[col] = dec_file[col].apply(_parse_mixed_date)

    if "variety" in dec_file.columns:
        dec_file["variety"] = dec_file["variety"].fillna("").astype(str).str.strip().replace("", pd.NA)
    if "decfile_ver" in dec_file.columns:
        dec_file["decfile_ver"] = dec_file["decfile_ver"].fillna("").astype(str).str.strip().replace("", pd.NA)
    if "decfile_type" in dec_file.columns:
        dec_file["decfile_type"] = dec_file["decfile_type"].fillna("").astype(str).str.strip().replace("", pd.NA)

    # Build a long-format defect list per training row
    defect_cols = [c for c in dec_file.columns if c.startswith("defects")]
    if defect_cols:
        def _row_defects(row):
            items = []
            for c in defect_cols:
                v = row.get(c)
                if pd.isna(v): continue
                v = str(v).strip()
                if v in ("", "-", "—"): continue
                # split on ; or , to handle "san_jose; (C6)scab"
                for piece in v.replace(";", ",").split(","):
                    piece = piece.strip()
                    if piece and piece not in ("-",):
                        items.append(piece)
            return items
        dec_file["defects_list"] = dec_file.apply(_row_defects, axis=1)
        dec_file["defect_count"] = dec_file["defects_list"].apply(len)

    # Turnaround: positive only; negative values indicate data-entry mistake (complete < submit)
    if "date_submit" in dec_file.columns and "date_complete" in dec_file.columns:
        dec_file["turnaround_days"] = (dec_file["date_complete"] - dec_file["date_submit"]).dt.days
        dec_file.loc[dec_file["turnaround_days"] < 0, "turnaround_days"] = pd.NA

    dec_file["status"] = dec_file["date_complete"].apply(
        lambda d: "Completed" if pd.notna(d) else "Pending"
    )

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
  <div class="page-header-left">
    <h1>🍎 Presizing <span>Operations</span></h1>
    <p class="subtitle">Apple Packing · Presizing Department · Production Intelligence Dashboard</p>
  </div>
  <div class="page-header-right">
    <span class="header-badge">LIVE DATA</span>
    <span class="header-meta">Last run: {date_str} &nbsp;·&nbsp; {len(runs):,} runs on record</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# NAVIGATION PANEL (dark navy bar) + page tabs + filters toggle
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="nav-panel"><div class="nav-panel-header"><span class="nav-panel-title">Navigation</span></div></div>', unsafe_allow_html=True)

# Page tabs as a horizontal radio
nav_col1, nav_col2 = st.columns([5, 1])
with nav_col1:
    page = st.radio(
        "Page",
        ["📊  Summary", "🎯  IQS", "🍏  Quality", "👷  Operators", "🧠  Training"],
        label_visibility="collapsed",
        horizontal=True,
        key="nav_page",
    )
with nav_col2:
    st.markdown('<div class="nav-toggle-btn-row">', unsafe_allow_html=True)
    toggle_label = "✕  HIDE FILTERS" if st.session_state.show_filters else "☰  SHOW FILTERS"
    if st.button(toggle_label, key="filters_toggle_btn", use_container_width=True):
        st.session_state.show_filters = not st.session_state.show_filters
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# FILTERS — shown only when show_filters is True
# Each page has its own context-aware filter set.
# ─────────────────────────────────────────────────────────────
if st.session_state.show_filters:
    st.markdown('<div class="filters-card"><div class="filters-card-title">Filters</div>', unsafe_allow_html=True)

    if page.endswith("Summary"):
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            period_choice = st.radio(
                "View by",
                ["Yearly", "Monthly", "Weekly"],
                horizontal=True,
                index=1,  # default to Monthly
                key="s_period",
            )
        summary_df = runs.dropna(subset=["run_date"]).copy()

        if period_choice == "Yearly":
            summary_df["year"] = summary_df["run_date"].dt.year.astype(int)
            available_years = sorted(summary_df["year"].dropna().unique(), reverse=True)
            with f2:
                selected_year = st.selectbox("📅  Year", available_years, key="s_year")

        elif period_choice == "Monthly":
            summary_df["year"] = summary_df["run_date"].dt.year.astype(int)
            summary_df["month_num"] = summary_df["run_date"].dt.month
            summary_df["month_name"] = summary_df["run_date"].dt.strftime("%b")
            summary_df["month_label"] = summary_df["run_date"].dt.to_period("M").astype(str)
            available_years = sorted(summary_df["year"].dropna().unique(), reverse=True)
            with f2:
                selected_year = st.selectbox("📅  Year", available_years, key="s_year_m")
            year_df = summary_df[summary_df["year"] == selected_year].copy()
            # Descending: most-recent month at top
            available_months = year_df["month_label"].dropna().drop_duplicates().sort_values(ascending=False).tolist()
            with f3:
                sel_month_raw = st.selectbox("📅  Month", ["All months"] + available_months, key="s_month")
            selected_month = None if sel_month_raw == "All months" else sel_month_raw

        else:  # Weekly
            summary_df["month_label"] = summary_df["run_date"].dt.to_period("M").astype(str)
            summary_df["week_start"] = summary_df["run_date"] - pd.to_timedelta(summary_df["run_date"].dt.weekday, unit="D")
            summary_df["week_label"] = "W/C " + summary_df["week_start"].dt.strftime("%Y-%m-%d")
            # Descending months
            available_months = summary_df["month_label"].dropna().drop_duplicates().sort_values(ascending=False).tolist()
            with f2:
                sel_month_raw = st.selectbox("📅  Month", ["All months"] + available_months, key="s_month_w")
            selected_month = None if sel_month_raw == "All months" else sel_month_raw
            month_df = summary_df.copy() if selected_month is None else summary_df[summary_df["month_label"] == selected_month].copy()
            # Descending weeks (most recent first)
            available_weeks = (
                month_df[["week_label","week_start"]]
                .drop_duplicates()
                .sort_values("week_start", ascending=False)["week_label"].tolist()
            )
            with f3:
                sel_week_raw = st.selectbox("📅  Week", ["All weeks"] + available_weeks, key="s_week")
            selected_week = None if sel_week_raw == "All weeks" else sel_week_raw

    elif page.endswith("Quality"):
        f1, f2, f3 = st.columns(3)
        quality_runs = runs.copy()
        quality_runs["month_label"] = quality_runs["run_date"].dt.to_period("M").astype(str)
        with f1:
            selected_variety = st.selectbox(
                "🍎  Variety",
                ["All varieties"] + sorted(quality_runs["variety"].dropna().astype(str).unique()),
                key="q_var",
            )
        with f2:
            selected_grower = st.selectbox(
                "🌿  Grower",
                ["All growers"] + sorted(quality_runs["grower"].dropna().astype(str).unique()),
                key="q_grower",
            )
        with f3:
            selected_quality_month = st.selectbox(
                "📅  Month",
                ["All months"] + sorted(quality_runs["month_label"].dropna().astype(str).unique(), reverse=True),
                key="q_month",
            )

    elif page.endswith("IQS"):
        if changes is not None:
            mode_df_pre = changes.copy()
            if "run_id" in mode_df_pre.columns and "run_id" in runs.columns:
                mode_df_pre = mode_df_pre.merge(
                    runs[["run_id","batch_id","grower","variety","run_date"]],
                    on="run_id", how="left", suffixes=("","_run")
                )
            if batches is not None and "batch_id" in mode_df_pre.columns and "batch_id" in batches.columns:
                bcols = [c for c in ["batch_id","grower","variety","decfile_version","defect_1","defect_2","defect_3"] if c in batches.columns]
                mode_df_pre = mode_df_pre.merge(batches[bcols], on="batch_id", how="left", suffixes=("","_batch"))
            for col in ["grower","variety","decfile_version","mode","check_class","reason","action","sensitivity","accuracy"]:
                if col in mode_df_pre.columns:
                    mode_df_pre[col] = mode_df_pre[col].fillna("").astype(str).str.strip().replace("", pd.NA)

            f1, f2, f3 = st.columns(3)
            with f1:
                av = ["All varieties"] + sorted(mode_df_pre["variety"].dropna().astype(str).unique()) if "variety" in mode_df_pre.columns else ["All varieties"]
                selected_mode_variety = st.selectbox("🍎  Variety", av, key="m_var")

            mode_temp = mode_df_pre.copy()
            if selected_mode_variety != "All varieties" and "variety" in mode_temp.columns:
                mode_temp = mode_temp[mode_temp["variety"].astype(str) == selected_mode_variety]

            with f2:
                ag = ["All growers"] + sorted(mode_temp["grower"].dropna().astype(str).unique()) if "grower" in mode_temp.columns else ["All growers"]
                selected_mode_grower = st.selectbox("🌿  Grower", ag, key="m_grower")
            if selected_mode_grower != "All growers" and "grower" in mode_temp.columns:
                mode_temp = mode_temp[mode_temp["grower"].astype(str) == selected_mode_grower]

            with f3:
                aver = ["All versions"] + sorted(mode_temp["decfile_version"].dropna().astype(str).unique()) if "decfile_version" in mode_temp.columns else ["All versions"]
                selected_version = st.selectbox("📋  Dec File Version", aver, key="m_ver")
        else:
            selected_mode_variety = "All varieties"
            selected_mode_grower = "All growers"
            selected_version = "All versions"

    elif page.endswith("Operators"):
        f1, f2 = st.columns(2)
        ops_pre = runs.copy()
        ops_pre["month_label"] = ops_pre["run_date"].dt.to_period("M").astype(str)
        with f1:
            month_opts = sorted(ops_pre["month_label"].dropna().astype(str).unique(), reverse=True)
            sel_op_month = st.selectbox("📅  Month", ["All months"] + month_opts, key="op_month")
        with f2:
            variety_opts = sorted(ops_pre["variety"].dropna().astype(str).unique()) if "variety" in ops_pre.columns else []
            sel_op_var = st.selectbox("🍎  Variety", ["All varieties"] + variety_opts, key="op_var")

    elif page.endswith("Training"):
        if dec_file is None or dec_file.empty:
            st.info("dec_file_raw.csv not found — Training filters unavailable.")
            sel_tr_year = "All years"; sel_tr_variety = "All varieties"; sel_tr_status = "All"
        else:
            f1, f2, f3 = st.columns(3)
            year_opts = sorted(
                dec_file["date_submit"].dropna().dt.year.astype(int).unique().tolist(),
                reverse=True
            )
            with f1:
                sel_tr_year = st.selectbox("📅  Year submitted", ["All years"] + [str(y) for y in year_opts], key="tr_year")
            with f2:
                tr_var_opts = sorted(dec_file["variety"].dropna().astype(str).unique().tolist())
                sel_tr_variety = st.selectbox("🍎  Variety", ["All varieties"] + tr_var_opts, key="tr_variety")
            with f3:
                sel_tr_status = st.selectbox("📋  Status", ["All", "Completed", "Pending"], key="tr_status")

    st.markdown('</div>', unsafe_allow_html=True)
else:
    # Filters hidden — still need to compute the values from session state defaults
    if page.endswith("Summary"):
        period_choice = st.session_state.get("s_period", "Yearly")
        summary_df = runs.dropna(subset=["run_date"]).copy()
        summary_df["year"] = summary_df["run_date"].dt.year.astype(int)
        if period_choice == "Yearly":
            available_years = sorted(summary_df["year"].dropna().unique(), reverse=True)
            selected_year = st.session_state.get("s_year", available_years[0] if available_years else None)
        elif period_choice == "Monthly":
            summary_df["month_num"] = summary_df["run_date"].dt.month
            summary_df["month_name"] = summary_df["run_date"].dt.strftime("%b")
            summary_df["month_label"] = summary_df["run_date"].dt.to_period("M").astype(str)
            available_years = sorted(summary_df["year"].dropna().unique(), reverse=True)
            selected_year = st.session_state.get("s_year_m", available_years[0] if available_years else None)
            year_df = summary_df[summary_df["year"] == selected_year].copy()
            available_months = year_df["month_label"].dropna().drop_duplicates().sort_values(ascending=False).tolist()
            sel_month_raw = st.session_state.get("s_month", "All months")
            selected_month = None if sel_month_raw == "All months" else sel_month_raw
        else:
            summary_df["month_label"] = summary_df["run_date"].dt.to_period("M").astype(str)
            summary_df["week_start"] = summary_df["run_date"] - pd.to_timedelta(summary_df["run_date"].dt.weekday, unit="D")
            summary_df["week_label"] = "W/C " + summary_df["week_start"].dt.strftime("%Y-%m-%d")
            available_months = summary_df["month_label"].dropna().drop_duplicates().sort_values(ascending=False).tolist()
            sel_month_raw = st.session_state.get("s_month_w", "All months")
            selected_month = None if sel_month_raw == "All months" else sel_month_raw
            month_df = summary_df.copy() if selected_month is None else summary_df[summary_df["month_label"] == selected_month].copy()
            available_weeks = (
                month_df[["week_label","week_start"]]
                .drop_duplicates()
                .sort_values("week_start", ascending=False)["week_label"].tolist()
            )
            sel_week_raw = st.session_state.get("s_week", "All weeks")
            selected_week = None if sel_week_raw == "All weeks" else sel_week_raw
    elif page.endswith("Quality"):
        quality_runs = runs.copy()
        quality_runs["month_label"] = quality_runs["run_date"].dt.to_period("M").astype(str)
        selected_variety = st.session_state.get("q_var", "All varieties")
        selected_grower = st.session_state.get("q_grower", "All growers")
        selected_quality_month = st.session_state.get("q_month", "All months")
    elif page.endswith("IQS"):
        selected_mode_variety = st.session_state.get("m_var", "All varieties")
        selected_mode_grower = st.session_state.get("m_grower", "All growers")
        selected_version = st.session_state.get("m_ver", "All versions")
    elif page.endswith("Operators"):
        sel_op_month = st.session_state.get("op_month", "All months")
        sel_op_var = st.session_state.get("op_var", "All varieties")
    elif page.endswith("Training"):
        sel_tr_year = st.session_state.get("tr_year", "All years")
        sel_tr_variety = st.session_state.get("tr_variety", "All varieties")
        sel_tr_status = st.session_state.get("tr_status", "All")

# ═══════════════════════════════════════════════════════════════
# SUMMARY PAGE
# ═══════════════════════════════════════════════════════════════
if page.endswith("Summary"):

    # Sub-page banner
    st.markdown('<div class="section-title">Production Summary</div>', unsafe_allow_html=True)

    def format_delta(current, previous, mode="number"):
        if pd.isna(current) or pd.isna(previous): return "N/A"
        if mode == "percent":
            if previous == 0: return "N/A"
            return f"{((current-previous)/previous)*100:+.1f}% vs prev"
        if mode == "float": return f"{current-previous:+.1f} vs prev"
        return f"{int(current-previous):+,.0f} vs prev"

    # ── Period slicing (filters come from sidebar) ───────────
    if period_choice == "Yearly":
        chart_df = summary_df.groupby("year", as_index=False)["bins_run"].sum().sort_values("year")
        summary_filtered = summary_df[summary_df["year"] == selected_year].copy()
        selected_period_label = str(selected_year)
        prev_year = selected_year - 1
        previous_filtered = summary_df[summary_df["year"] == prev_year].copy()
        prev_month = prev_week = None

    elif period_choice == "Monthly":
        year_df = summary_df[summary_df["year"] == selected_year].copy()
        chart_df = (summary_df.groupby(["year","month_num","month_name"], as_index=False)["bins_run"]
                    .sum().sort_values(["month_num","year"], ascending=[True, False]))
        if selected_month is None:
            summary_filtered = year_df.copy()
            selected_period_label = f"{selected_year} (All months)"
            previous_filtered = pd.DataFrame()
            prev_month = None
        else:
            summary_filtered = year_df[year_df["month_label"] == selected_month].copy()
            selected_period_label = selected_month
            idx = available_months.index(selected_month)
            prev_month = available_months[idx-1] if idx > 0 else None
            previous_filtered = year_df[year_df["month_label"] == prev_month].copy() if prev_month else pd.DataFrame()
        prev_week = None
        prev_year = None

    else:  # Weekly
        month_df = summary_df.copy() if selected_month is None else summary_df[summary_df["month_label"] == selected_month].copy()
        chart_df = month_df.groupby(["week_label","week_start"], as_index=False)["bins_run"].sum().sort_values("week_start")
        if selected_week is None:
            summary_filtered = month_df.copy()
            selected_period_label = f"{selected_month} (All weeks)" if selected_month else "All weeks"
            previous_filtered = pd.DataFrame()
            prev_week = None
        else:
            summary_filtered = month_df[month_df["week_label"] == selected_week].copy()
            selected_period_label = selected_week
            idx = available_weeks.index(selected_week)
            prev_week = available_weeks[idx-1] if idx > 0 else None
            previous_filtered = month_df[month_df["week_label"] == prev_week].copy() if prev_week else pd.DataFrame()
        prev_month = None
        prev_year = None

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
            cur_dt = dtf[dtf["month_label"] == selected_month] if selected_month else dtf[dtf["year"] == selected_year]
            prv_dt = dtf[dtf["month_label"] == prev_month] if (selected_month and prev_month) else pd.DataFrame()
        else:
            dtf["week_label"] = "W/C " + (dtf["run_date"] - pd.to_timedelta(dtf["run_date"].dt.weekday, unit="D")).dt.strftime("%Y-%m-%d")
            cur_dt = dtf[dtf["week_label"] == selected_week] if selected_week else dtf
            prv_dt = dtf[dtf["week_label"] == prev_week] if (selected_week and prev_week) else pd.DataFrame()
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

        fig.update_traces(hovertemplate="%{y:,.0f} bins<extra></extra>", name="")
        fig.update_layout(showlegend=(period_choice == "Monthly"))
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

    # ── Bins/Hour by Grower bar chart — scoped to selected period ──
    if "bins_per_hour_row" in summary_filtered.columns:
        st.markdown(
            f'<div class="section-title">Throughput Efficiency by Grower — {selected_period_label}</div>',
            unsafe_allow_html=True
        )
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
                             color="bins_per_hour", color_continuous_scale=["#1e2435", BLUE],
                             labels={"bins_per_hour": "Bins/hr", "grower": "Grower"})
            if overall_bph:
                fig_bph.add_vline(x=overall_bph, line_dash="dot", line_color=ROSE,
                                  annotation_text=f"Avg {overall_bph:.1f}", annotation_font_color=ROSE)
            fig_bph.update_coloraxes(showscale=False)
            fig_bph.update_traces(hovertemplate="%{x:.1f} bins/hr<extra></extra>", name="")
            apply_plot_theme(fig_bph, height=max(280, len(bph_grower)*32))
            st.plotly_chart(fig_bph, use_container_width=True)
        else:
            st.info(f"No throughput data available for {selected_period_label}.")

    st.markdown("---")

    # ── Variety deep-dive ───────────────────────────────────
    st.markdown('<div class="section-title">Variety Deep-Dive</div>', unsafe_allow_html=True)
    available_varieties = sorted(summary_filtered["variety"].dropna().astype(str).unique().tolist())
    sv1, sv2 = st.columns([1, 4])
    with sv1:
        selected_summary_variety = st.selectbox("🍎  Variety", available_varieties or ["No data"], key="sum_var")
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
# QUALITY PAGE
# ═══════════════════════════════════════════════════════════════
elif page.endswith("Quality"):
    st.markdown('<div class="section-title">Quality Performance</div>', unsafe_allow_html=True)

    quality_filtered = quality_runs.copy()
    if selected_variety != "All varieties": quality_filtered = quality_filtered[quality_filtered["variety"].astype(str) == selected_variety]
    if selected_grower != "All growers":  quality_filtered = quality_filtered[quality_filtered["grower"].astype(str) == selected_grower]
    if selected_quality_month != "All months": quality_filtered = quality_filtered[quality_filtered["month_label"].astype(str) == selected_quality_month]

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
        if selected_variety != "All varieties" and "variety" in batch_filtered.columns:
            batch_filtered = batch_filtered[batch_filtered["variety"].astype(str) == selected_variety]
        if selected_grower != "All growers" and "grower" in batch_filtered.columns:
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
        if selected_variety != "All varieties" and "variety" in ch.columns:
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
# IQS PAGE  (Image Quality System — was "Mode")
# ═══════════════════════════════════════════════════════════════
elif page.endswith("IQS"):
    st.markdown('<div class="section-title">IQS Boundary Analysis</div>', unsafe_allow_html=True)

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

        # Apply filters from sidebar — filtered_mode = exact (variety+grower+version)
        filtered_mode = mode_df.copy()
        if selected_mode_variety != "All varieties" and "variety" in filtered_mode.columns:
            filtered_mode = filtered_mode[filtered_mode["variety"].astype(str) == selected_mode_variety]
        if selected_mode_grower != "All growers" and "grower" in filtered_mode.columns:
            filtered_mode = filtered_mode[filtered_mode["grower"].astype(str) == selected_mode_grower]
        if selected_version != "All versions" and "decfile_version" in filtered_mode.columns:
            filtered_mode = filtered_mode[filtered_mode["decfile_version"].astype(str) == selected_version]

        # variety_pool = same variety, ALL growers (for reference boundaries)
        variety_pool = mode_df.copy()
        if selected_mode_variety != "All varieties" and "variety" in variety_pool.columns:
            variety_pool = variety_pool[variety_pool["variety"].astype(str) == selected_mode_variety]
        if selected_version != "All versions" and "decfile_version" in variety_pool.columns:
            variety_pool = variety_pool[variety_pool["decfile_version"].astype(str) == selected_version]

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

        # ── Selection context (left) + Top Defects chart (right) ──────
        ctx_left, ctx_right = st.columns([1, 1.4])

        with ctx_left:
            st.markdown('<div class="section-title">Current Selection</div>', unsafe_allow_html=True)

            # build defect list for this variety+grower
            current_defects = []
            if batches is not None:
                fbm = batches.copy()
                for col in ["grower","variety","decfile_version","defect_1","defect_2","defect_3"]:
                    if col in fbm.columns:
                        fbm[col] = fbm[col].fillna("").astype(str).str.strip().replace("", pd.NA)
                if selected_mode_variety != "All varieties" and "variety" in fbm.columns:
                    fbm = fbm[fbm["variety"].astype(str) == selected_mode_variety]
                if selected_mode_grower != "All growers" and "grower" in fbm.columns:
                    fbm = fbm[fbm["grower"].astype(str) == selected_mode_grower]
                dcols = [c for c in ["defect_1","defect_2","defect_3"] if c in fbm.columns]
                if dcols:
                    md_all = fbm[dcols].melt(value_name="d")["d"].dropna().astype(str).str.strip()
                    md_all = md_all[md_all != ""]
                    current_defects = md_all.value_counts().index.tolist()

            # version display
            ver_text = selected_version if selected_version != "All versions" else "—"
            batch_count = len(batches[
                (batches.get("variety", "").astype(str) == selected_mode_variety) &
                (batches.get("grower", "").astype(str) == selected_mode_grower)
            ]) if (batches is not None and selected_mode_variety != "All varieties" and selected_mode_grower != "All growers") else "—"

            # KPI-style context cards
            st.markdown(f"""
              <div class="kpi-card">
                <div class="kpi-label">Variety</div>
                <div class="kpi-value" style="font-family:'Inter',sans-serif;text-transform:capitalize;">
                  {selected_mode_variety.replace('_',' ') if selected_mode_variety != "All varieties" else "All varieties"}
                </div>
              </div>
              <div class="kpi-card">
                <div class="kpi-label">Grower</div>
                <div class="kpi-value" style="font-family:'Inter',sans-serif;text-transform:capitalize;">
                  {selected_mode_grower.replace('_',' ') if selected_mode_grower != "All growers" else "All growers"}
                </div>
              </div>
              <div class="kpi-card">
                <div class="kpi-label">Dec File Version &nbsp;·&nbsp; Batches</div>
                <div class="kpi-value" style="font-family:'Inter',sans-serif;font-size:1.2rem;">
                  {ver_text} &nbsp;·&nbsp; {batch_count if batch_count != "—" else "—"} batches
                </div>
              </div>
            """, unsafe_allow_html=True)

            # Defect chips inline, in descending order
            if current_defects:
                chips_html = "".join([f'<span class="insight-tag">{d}</span>' for d in current_defects[:12]])
                st.markdown(f"""
                  <div style="margin-top:8px;">
                    <div class="kpi-label" style="margin-bottom:8px;">Recorded Defects (most → least)</div>
                    {chips_html}
                  </div>
                """, unsafe_allow_html=True)

        with ctx_right:
            st.markdown('<div class="section-title">Top Defects for Selection</div>', unsafe_allow_html=True)

            top_defects_mode = pd.DataFrame(columns=["Defect","Count"])
            if batches is not None:
                bm = batches.copy()
                for col in ["grower","variety","decfile_version","defect_1","defect_2","defect_3"]:
                    if col in bm.columns:
                        bm[col] = bm[col].fillna("").astype(str).str.strip().replace("", pd.NA)
                fbm = bm.copy()
                if selected_mode_variety != "All varieties" and "variety" in fbm.columns:
                    fbm = fbm[fbm["variety"].astype(str) == selected_mode_variety]
                if selected_mode_grower != "All growers" and "grower" in fbm.columns:
                    fbm = fbm[fbm["grower"].astype(str) == selected_mode_grower]
                dcols = [c for c in ["defect_1","defect_2","defect_3"] if c in fbm.columns]
                if dcols:
                    md = fbm[dcols].melt(value_name="defect")["defect"].dropna().astype(str).str.strip()
                    md = md[md != ""]
                    if not md.empty:
                        top_defects_mode = md.value_counts().reset_index()
                        top_defects_mode.columns = ["Defect","Count"]

            if not top_defects_mode.empty:
                tdm_sorted = top_defects_mode.head(10).sort_values("Count", ascending=True)  # ascending for h-bar so largest is at top
                fig_tdm = px.bar(
                    tdm_sorted, x="Count", y="Defect", orientation="h",
                    text="Count", color_discrete_sequence=[BLUE]
                )
                fig_tdm.update_traces(
                    textposition="outside",
                    textfont=dict(family="DM Mono, monospace", size=12, color="#0f1d35"),
                    hovertemplate="%{y}<br>Count: %{x}<extra></extra>",
                    cliponaxis=False,
                    name=""  # remove "undefined" trace name
                )
                fig_tdm.update_layout(
                    title=None,
                    showlegend=False,
                    xaxis_title=None, yaxis_title=None,
                    yaxis=dict(tickfont=dict(size=12, color="#2d3f5e"))
                )
                apply_plot_theme(fig_tdm, height=max(320, 38 * len(tdm_sorted)))
                # add headroom for outside text
                fig_tdm.update_xaxes(range=[0, tdm_sorted["Count"].max() * 1.15])
                st.plotly_chart(fig_tdm, use_container_width=True)
            else:
                st.info("No defect data for current filters.")

        st.markdown("---")

        # ── Top Adjusted Modes table — reordered columns ─────────────
        st.markdown('<div class="section-title">Top Adjusted Modes</div>', unsafe_allow_html=True)
        st.caption("**Boundaries** = after-boundaries recorded for *this* grower + variety.  **Reference Boundaries** = after-boundaries seen for *the same variety across all growers* (broader reference pool).")

        adjusted_mode_table = pd.DataFrame()
        if "mode" in filtered_mode.columns and "action" in filtered_mode.columns:
            adjusted = filtered_mode[filtered_mode["action"].astype(str).str.lower().str.startswith("a")].copy()

            # reference adjusted pool (same variety, all growers)
            variety_adjusted = variety_pool.copy()
            if "action" in variety_adjusted.columns:
                variety_adjusted = variety_adjusted[
                    variety_adjusted["action"].astype(str).str.lower().str.startswith("a")
                ]

            if not adjusted.empty:
                rows = []
                gcols = ["mode"] + (["check_class"] if "check_class" in adjusted.columns else [])
                for keys, grp in adjusted.groupby(gcols, dropna=False):
                    mode_name  = keys[0] if isinstance(keys, tuple) else keys
                    check_class = keys[1] if isinstance(keys, tuple) and len(keys) > 1 else ""

                    # Boundaries — for this grower+variety
                    _, own_b = summarize_boundaries(grp["boundary_after"]) if "boundary_after" in grp.columns else ("","")

                    # Reference Boundaries — for same variety, all growers
                    ref_grp = variety_adjusted
                    if "mode" in ref_grp.columns:
                        ref_grp = ref_grp[ref_grp["mode"].astype(str) == str(mode_name)]
                    if "check_class" in ref_grp.columns and check_class:
                        ref_grp = ref_grp[ref_grp["check_class"].astype(str) == str(check_class)]
                    _, ref_b = summarize_boundaries(ref_grp["boundary_after"]) if "boundary_after" in ref_grp.columns else ("","")

                    sensitivity_text = ", ".join(sorted(set(grp["sensitivity"].dropna().astype(str)))) if "sensitivity" in grp.columns else ""
                    accuracy_text    = ", ".join(sorted(set(grp["accuracy"].dropna().astype(str)))) if "accuracy" in grp.columns else ""

                    rows.append({
                        "Check": False,
                        "Mode": mode_name,
                        "Check Class": check_class,
                        "Boundaries": own_b,
                        "Reference Boundaries": ref_b,
                        "Count": len(grp),
                        "Sensitivity": sensitivity_text,
                        "Accuracy": accuracy_text,
                    })
                adjusted_mode_table = (
                    pd.DataFrame(rows)
                    .sort_values(["Count","Mode"], ascending=[False, True])
                    .reset_index(drop=True)
                )

        if not adjusted_mode_table.empty:
            st.data_editor(
                adjusted_mode_table,
                use_container_width=True, height=320, hide_index=True,
                column_config={
                    "Check": st.column_config.CheckboxColumn("✓", width="small"),
                    "Mode": st.column_config.TextColumn("Mode", width="medium"),
                    "Check Class": st.column_config.TextColumn("Check Class", width="small"),
                    "Boundaries": st.column_config.TextColumn("Boundaries", width="medium",
                        help="After-boundaries recorded for this grower + variety"),
                    "Reference Boundaries": st.column_config.TextColumn("Reference Boundaries", width="large",
                        help="After-boundaries recorded for the same variety across all growers"),
                    "Count": st.column_config.NumberColumn("Count", width="small"),
                    "Sensitivity": st.column_config.TextColumn("Sensitivity", width="small"),
                    "Accuracy": st.column_config.TextColumn("Accuracy", width="small"),
                },
                column_order=["Check", "Mode", "Check Class", "Boundaries",
                              "Reference Boundaries", "Count", "Sensitivity", "Accuracy"],
                disabled=["Mode","Check Class","Boundaries","Reference Boundaries","Count","Sensitivity","Accuracy"],
                key="adj_mode_editor"
            )
        else:
            st.info("No adjusted mode data.")

        st.markdown("---")

        # ── Defect Investigation Workflow — bidirectional ─────────
        st.markdown('<div class="section-title">Defect Investigation Workflow</div>', unsafe_allow_html=True)

        flow_dir = st.radio(
            "Investigation direction",
            ["🐛  Defect → ⚙️ Mode", "⚙️  Mode → 🐛 Defect"],
            horizontal=True,
            key="m_flow_dir"
        )
        is_defect_first = flow_dir.startswith("🐛")

        # Build option lists
        available_reason_items = []
        if "reason" in filtered_mode.columns:
            sr = filtered_mode["reason"].dropna().astype(str).str.split(",").explode().astype(str).str.strip()
            available_reason_items = sorted(sr[sr != ""].unique().tolist())

        available_mode_items = []
        if "mode" in filtered_mode.columns:
            available_mode_items = sorted(filtered_mode["mode"].dropna().astype(str).unique().tolist())

        st.markdown("")  # spacer

        step_l, step_r = st.columns(2)

        if is_defect_first:
            # ───── Defect → Mode flow ─────
            with step_l:
                st.markdown("**Step 1 — Choose a defect / reason**")
                selected_reason = st.selectbox(
                    "🐛  Defect / Reason",
                    ["Select a defect…"] + available_reason_items,
                    key="m_reason_df",
                )

                related_modes = pd.DataFrame()
                if selected_reason != "Select a defect…":
                    rdf = filtered_mode.copy()
                    rdf["reason_item"] = rdf["reason"].fillna("").astype(str).str.split(",")
                    rdf = rdf.explode("reason_item")
                    rdf["reason_item"] = rdf["reason_item"].astype(str).str.strip()
                    rdf = rdf[rdf["reason_item"] == selected_reason].copy()

                    if not rdf.empty:
                        rows = []
                        for keys, grp in rdf.groupby(["mode","check_class"], dropna=False):
                            _, allb = summarize_boundaries(grp["boundary_after"]) if "boundary_after" in grp.columns else ("","")
                            rows.append({
                                "Mode": keys[0],
                                "Check Class": keys[1],
                                "Boundaries": allb,
                                "Count": len(grp),
                            })
                        related_modes = pd.DataFrame(rows).sort_values("Count", ascending=False)

                if not related_modes.empty:
                    st.dataframe(related_modes, use_container_width=True, height=260, hide_index=True)
                elif selected_reason != "Select a defect…":
                    st.info("No related modes found.")
                else:
                    st.info("Pick a defect to see which modes detect it.")

            with step_r:
                st.markdown("**Step 2 — Pick a mode → see what else it detects**")
                mode_options = related_modes["Mode"].dropna().astype(str).unique().tolist() if not related_modes.empty else []
                selected_related_mode = st.selectbox(
                    "⚙️  Mode",
                    ["Select a mode…"] + sorted(mode_options),
                    key="m_rel_mode_df"
                )

                if selected_related_mode != "Select a mode…":
                    sel_mode_rows = filtered_mode[filtered_mode["mode"].astype(str) == selected_related_mode].copy()
                    if "reason" in sel_mode_rows.columns:
                        other_reasons = (sel_mode_rows["reason"].dropna().astype(str).str.split(",")
                                         .explode().astype(str).str.strip())
                        other_reasons = other_reasons[other_reasons != ""]
                        if not other_reasons.empty:
                            orc = other_reasons.value_counts().reset_index()
                            orc.columns = ["Recorded Reason","Count"]
                            st.dataframe(orc, use_container_width=True, height=260, hide_index=True)
                        else:
                            st.info("No other recorded reasons.")
                else:
                    st.info("Select a mode from Step 1 to inspect.")

        else:
            # ───── Mode → Defect flow ─────
            with step_l:
                st.markdown("**Step 1 — Choose a mode**")
                selected_mode_first = st.selectbox(
                    "⚙️  Mode",
                    ["Select a mode…"] + available_mode_items,
                    key="m_mode_md",
                )

                related_defects = pd.DataFrame()
                if selected_mode_first != "Select a mode…":
                    sel_rows = filtered_mode[filtered_mode["mode"].astype(str) == selected_mode_first].copy()
                    if "reason" in sel_rows.columns:
                        rd = (sel_rows["reason"].dropna().astype(str).str.split(",")
                              .explode().astype(str).str.strip())
                        rd = rd[rd != ""]
                        if not rd.empty:
                            related_defects = rd.value_counts().reset_index()
                            related_defects.columns = ["Defect / Reason","Count"]

                if not related_defects.empty:
                    st.dataframe(related_defects, use_container_width=True, height=260, hide_index=True)
                elif selected_mode_first != "Select a mode…":
                    st.info("No defects logged against this mode for the current selection.")
                else:
                    st.info("Pick a mode to see which defects it captures.")

            with step_r:
                st.markdown("**Step 2 — Pick a defect → see all modes that detect it**")
                defect_options = related_defects["Defect / Reason"].astype(str).tolist() if not related_defects.empty else []
                selected_defect_md = st.selectbox(
                    "🐛  Defect / Reason",
                    ["Select a defect…"] + defect_options,
                    key="m_defect_md"
                )

                if selected_defect_md != "Select a defect…":
                    rdf = filtered_mode.copy()
                    rdf["reason_item"] = rdf["reason"].fillna("").astype(str).str.split(",")
                    rdf = rdf.explode("reason_item")
                    rdf["reason_item"] = rdf["reason_item"].astype(str).str.strip()
                    rdf = rdf[rdf["reason_item"] == selected_defect_md].copy()

                    if not rdf.empty:
                        rows = []
                        for keys, grp in rdf.groupby(["mode","check_class"], dropna=False):
                            _, allb = summarize_boundaries(grp["boundary_after"]) if "boundary_after" in grp.columns else ("","")
                            rows.append({
                                "Mode": keys[0],
                                "Check Class": keys[1],
                                "Boundaries": allb,
                                "Count": len(grp),
                            })
                        out_df = pd.DataFrame(rows).sort_values("Count", ascending=False)
                        st.dataframe(out_df, use_container_width=True, height=260, hide_index=True)
                    else:
                        st.info("No modes found for this defect.")
                else:
                    st.info("Select a defect from Step 1 to inspect.")

        # ── Unchecked modes (separate section at bottom) ─────────
        st.markdown("---")
        st.markdown('<div class="section-title">Unchecked Modes for This Grower / Variety</div>', unsafe_allow_html=True)
        st.caption("Modes seen for this **variety** across other growers, but not yet checked or adjusted for the **current grower**.")

        next_modes_table = pd.DataFrame()
        if selected_mode_variety != "All varieties" and selected_mode_grower != "All growers":
            variety_mode_db = mode_df.copy()
            if "variety" in variety_mode_db.columns:
                variety_mode_db = variety_mode_db[variety_mode_db["variety"].astype(str) == selected_mode_variety]
            if selected_version != "All versions" and "decfile_version" in variety_mode_db.columns:
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
                rows.append({"Check": False, "Mode": mn, "Check Class": cc,
                             "Reference Boundaries": allb, "Count": len(grp)})

            if rows:
                next_modes_table = pd.DataFrame(rows).sort_values("Count", ascending=False).reset_index(drop=True)

        if selected_mode_variety == "All varieties" or selected_mode_grower == "All growers":
            st.info("Select a specific variety **and** grower in the sidebar to see unchecked modes.")
        elif not next_modes_table.empty:
            st.data_editor(
                next_modes_table, use_container_width=True, height=300, hide_index=True,
                column_config={
                    "Check": st.column_config.CheckboxColumn("✓", width="small"),
                    "Mode": st.column_config.TextColumn("Mode", width="medium"),
                    "Check Class": st.column_config.TextColumn("Check Class", width="small"),
                    "Reference Boundaries": st.column_config.TextColumn("Reference Boundaries", width="large"),
                    "Count": st.column_config.NumberColumn("Count", width="small"),
                },
                column_order=["Check","Mode","Check Class","Reference Boundaries","Count"],
                disabled=["Mode","Check Class","Reference Boundaries","Count"],
                key="unchecked_mode_editor"
            )
        else:
            st.info("No additional unchecked modes for this grower under the selected variety.")

# ═══════════════════════════════════════════════════════════════
# OPERATORS PAGE
# ═══════════════════════════════════════════════════════════════
elif page.endswith("Operators"):
    st.markdown('<div class="section-title">Shift Performance & Operating Rhythm</div>', unsafe_allow_html=True)
    st.caption("Insights about how shifts run — throughput consistency, lane balance, downtime impact, and daily rhythm. Operator names are shown alongside, but the focus is on the shift, not blame.")

    ops_df = runs.copy()
    has_machine  = "operator_machine"  in ops_df.columns
    has_quality  = "operator_quality"  in ops_df.columns

    # Filters
    ops_df["month_label"] = ops_df["run_date"].dt.to_period("M").astype(str)
    if sel_op_month != "All months":
        ops_df = ops_df[ops_df["month_label"] == sel_op_month]
    if sel_op_var != "All varieties" and "variety" in ops_df.columns:
        ops_df = ops_df[ops_df["variety"].astype(str) == sel_op_var]

    if ops_df.empty:
        st.info("No runs in the selected period.")
    else:
        # ── KPI strip ─────────────────────────────────────────
        n_runs     = len(ops_df)
        n_days     = ops_df["run_date"].dt.normalize().nunique()
        runs_per_day = n_runs / n_days if n_days else 0
        avg_run_hr = ops_df["run_hours"].mean() if "run_hours" in ops_df.columns else None
        med_run_hr = ops_df["run_hours"].median() if "run_hours" in ops_df.columns else None
        avg_bph    = (ops_df["total_bins_with_retip"].sum() / ops_df["run_hours"].sum()) \
                     if ("run_hours" in ops_df.columns and ops_df["run_hours"].sum() > 0) else None

        ko1, ko2, ko3, ko4 = st.columns(4)
        ko1.markdown(kpi_html("Total Runs", f"{n_runs:,}"), unsafe_allow_html=True)
        ko2.markdown(kpi_html("Active Days", f"{n_days:,}", f"{runs_per_day:.1f} runs/day"), unsafe_allow_html=True)
        ko3.markdown(kpi_html("Avg Run Length", f"{avg_run_hr:.1f} hr" if avg_run_hr else "N/A",
                              f"median {med_run_hr:.1f}" if med_run_hr else ""), unsafe_allow_html=True)
        ko4.markdown(kpi_html("Avg Bins / Hour", f"{avg_bph:.1f}" if avg_bph else "N/A"), unsafe_allow_html=True)

        st.markdown("---")

        # ── Daily throughput rhythm ───────────────────────────
        st.markdown('<div class="section-title">Daily Throughput Rhythm</div>', unsafe_allow_html=True)
        st.caption("How consistent is daily output? Spikes and dips reveal good days, breakdown days, or staffing changes.")
        daily = (ops_df.groupby(ops_df["run_date"].dt.normalize())
                       .agg(bins_run=("bins_run","sum"),
                            runs=("run_id","count") if "run_id" in ops_df.columns else ("bins_run","count"),
                            hours=("run_hours","sum"))
                       .reset_index().rename(columns={"run_date":"day"}))
        if not daily.empty:
            avg_bins_day = daily["bins_run"].mean()
            fig_daily = px.bar(daily, x="day", y="bins_run",
                               color_discrete_sequence=[BLUE],
                               labels={"day":"Date","bins_run":"Bins"})
            fig_daily.add_hline(y=avg_bins_day, line_dash="dot", line_color=ROSE,
                                annotation_text=f"Avg {avg_bins_day:.0f} bins/day",
                                annotation_font_color=ROSE, annotation_position="top right")
            fig_daily.update_traces(hovertemplate="%{x|%a %d %b}<br>%{y:,.0f} bins<extra></extra>", name="")
            apply_plot_theme(fig_daily, height=320)
            fig_daily.update_layout(showlegend=False, xaxis_title=None)
            st.plotly_chart(fig_daily, use_container_width=True)

        st.markdown("---")

        # ── Run-length distribution + start-time pattern ───────
        rl_left, rl_right = st.columns(2)

        with rl_left:
            st.markdown('<div class="section-title">Run Length Distribution</div>', unsafe_allow_html=True)
            st.caption("Are runs typically short or long? Wide spread = inconsistent shift planning.")
            if "run_hours" in ops_df.columns and ops_df["run_hours"].notna().any():
                fig_rl = px.histogram(ops_df.dropna(subset=["run_hours"]),
                                      x="run_hours", nbins=24,
                                      color_discrete_sequence=[BLUE],
                                      labels={"run_hours":"Run length (hours)"})
                fig_rl.update_traces(hovertemplate="%{x:.1f}h: %{y} runs<extra></extra>", name="")
                apply_plot_theme(fig_rl, height=300)
                fig_rl.update_layout(showlegend=False, yaxis_title="Runs")
                st.plotly_chart(fig_rl, use_container_width=True)
            else:
                st.info("Run length not available.")

        with rl_right:
            st.markdown('<div class="section-title">Start-Time Pattern</div>', unsafe_allow_html=True)
            st.caption("When do shifts typically begin? Reveals early/late starts and shift changeovers.")
            if "start_dt" in ops_df.columns and ops_df["start_dt"].notna().any():
                start_hours = ops_df["start_dt"].dt.hour.dropna()
                hourly = start_hours.value_counts().reindex(range(24), fill_value=0).reset_index()
                hourly.columns = ["hour","starts"]
                fig_st = px.bar(hourly, x="hour", y="starts",
                                color_discrete_sequence=[NAVY],
                                labels={"hour":"Hour of day","starts":"Run starts"})
                fig_st.update_traces(hovertemplate="%{x:02d}:00 — %{y} runs<extra></extra>", name="")
                apply_plot_theme(fig_st, height=300)
                fig_st.update_layout(showlegend=False, xaxis=dict(tickmode='linear', dtick=2))
                st.plotly_chart(fig_st, use_container_width=True)
            else:
                st.info("Start time not available.")

        st.markdown("---")

        # ── Lane Speed Balance ────────────────────────────────
        if speed_cols and any(c in ops_df.columns for c in speed_cols):
            st.markdown('<div class="section-title">Lane Speed Balance</div>', unsafe_allow_html=True)
            st.caption("Box plots of programmed speeds per lane group. A wide box = inconsistent setup; outliers = unusual runs to investigate.")
            speed_df = ops_df[speed_cols].melt(var_name="Lane", value_name="Speed").dropna()
            speed_df["Lane"] = speed_df["Lane"].map({
                "Speed_12":"Lanes 1-2","Speed_34":"Lanes 3-4","Speed_56":"Lanes 5-6","full_speed":"Full Speed"
            })
            if not speed_df.empty:
                fig_spd = px.box(speed_df, x="Lane", y="Speed", color="Lane",
                                 color_discrete_sequence=COLOR_SEQ,
                                 labels={"Speed":"Speed","Lane":"Lane Group"})
                fig_spd.update_traces(hovertemplate="%{y}<extra>%{x}</extra>")
                apply_plot_theme(fig_spd, height=320)
                fig_spd.update_layout(showlegend=False)
                st.plotly_chart(fig_spd, use_container_width=True)
            else:
                st.info("No lane speed values recorded for this period.")

        st.markdown("---")

        # ── Downtime impact on shift ──────────────────────────
        st.markdown('<div class="section-title">Downtime Impact on Shifts</div>', unsafe_allow_html=True)
        st.caption("Total downtime hours per day for the selected period — reveals which days lost the most production.")
        if downtime is not None and "run_date" in downtime.columns:
            dt_in = downtime.dropna(subset=["run_date"]).copy()
            dt_in["month_label"] = dt_in["run_date"].dt.to_period("M").astype(str)
            if sel_op_month != "All months":
                dt_in = dt_in[dt_in["month_label"] == sel_op_month]
            if not dt_in.empty:
                dt_daily = (dt_in.groupby(dt_in["run_date"].dt.normalize())["duration_hours"]
                                .sum().reset_index().rename(columns={"run_date":"day"}))
                fig_dt = px.bar(dt_daily, x="day", y="duration_hours",
                                color_discrete_sequence=[ROSE],
                                labels={"day":"Date","duration_hours":"Downtime (hr)"})
                fig_dt.update_traces(hovertemplate="%{x|%a %d %b}<br>%{y:.2f} hr<extra></extra>", name="")
                apply_plot_theme(fig_dt, height=280)
                fig_dt.update_layout(showlegend=False, xaxis_title=None)
                st.plotly_chart(fig_dt, use_container_width=True)
            else:
                st.info("No downtime recorded for this period.")
        else:
            st.info("downtime_raw.csv not available.")

        st.markdown("---")

        # ── Variety mix per shift ─────────────────────────────
        st.markdown('<div class="section-title">Variety Mix Handled</div>', unsafe_allow_html=True)
        st.caption("How many varieties did the shift switch between? Frequent variety changes mean more setup time and re-calibration.")
        if "variety" in ops_df.columns:
            vmix = (ops_df.groupby(ops_df["run_date"].dt.normalize())["variety"]
                          .nunique().reset_index().rename(columns={"run_date":"day", "variety":"varieties"}))
            if not vmix.empty:
                changeover_days = (vmix["varieties"] >= 2).sum()
                avg_var_day = vmix["varieties"].mean()

                vc1, vc2 = st.columns([1, 2])
                with vc1:
                    st.markdown(kpi_html("Days with 2+ Varieties", f"{changeover_days}",
                                         f"{changeover_days / len(vmix) * 100:.0f}% of active days" if len(vmix) else ""),
                                unsafe_allow_html=True)
                    st.markdown(kpi_html("Avg Varieties / Day", f"{avg_var_day:.1f}"),
                                unsafe_allow_html=True)
                with vc2:
                    fig_vmix = px.bar(vmix, x="day", y="varieties",
                                      color_discrete_sequence=[NAVY],
                                      labels={"day":"Date","varieties":"# Varieties"})
                    fig_vmix.update_traces(hovertemplate="%{x|%a %d %b}<br>%{y} varieties<extra></extra>", name="")
                    apply_plot_theme(fig_vmix, height=260)
                    fig_vmix.update_layout(showlegend=False, xaxis_title=None,
                                           yaxis=dict(tickmode='linear', dtick=1))
                    st.plotly_chart(fig_vmix, use_container_width=True)

        # ── Operator presence (only if data exists) ───────────
        op_present = pd.DataFrame()
        if has_machine or has_quality:
            rows = []
            for col in [c for c in ["operator_machine","operator_quality"] if c in ops_df.columns]:
                vc = ops_df[col].dropna().astype(str).value_counts()
                for name, cnt in vc.items():
                    if name.strip():
                        rows.append({"Role": col.replace("operator_","").title(), "Operator": name, "Runs": cnt})
            op_present = pd.DataFrame(rows)
        if not op_present.empty:
            st.markdown("---")
            st.markdown('<div class="section-title">Operator Coverage</div>', unsafe_allow_html=True)
            st.caption("Who was on shift during the selected period — by role.")
            st.dataframe(op_present.sort_values(["Role","Runs"], ascending=[True, False]),
                         use_container_width=True, hide_index=True, height=180)


# ═══════════════════════════════════════════════════════════════
# TRAINING PAGE  (dec_file training records)
# ═══════════════════════════════════════════════════════════════
elif page.endswith("Training"):
    st.markdown('<div class="section-title">Dec File Training Records</div>', unsafe_allow_html=True)
    st.caption("Each row in dec_file_raw.csv is a training submission for the IQS defect detector. This page tracks training velocity, turnaround, defect coverage, and how training maps to live runs.")

    if dec_file is None or dec_file.empty:
        st.info("dec_file_raw.csv not found. Place it in the same directory as the dashboard and reload.")
    else:
        # ── Apply filters from sidebar ────────────────────────
        tr_df = dec_file.copy()
        if sel_tr_year != "All years" and "date_submit" in tr_df.columns:
            tr_df = tr_df[tr_df["date_submit"].dt.year.astype("Int64").astype(str) == sel_tr_year]
        if sel_tr_variety != "All varieties" and "variety" in tr_df.columns:
            tr_df = tr_df[tr_df["variety"].astype(str) == sel_tr_variety]
        if sel_tr_status != "All" and "status" in tr_df.columns:
            tr_df = tr_df[tr_df["status"] == sel_tr_status]

        if tr_df.empty:
            st.info("No training records match the current filters.")
        else:
            # ── KPI strip ─────────────────────────────────────
            n_total     = len(tr_df)
            n_completed = (tr_df["status"] == "Completed").sum()
            n_pending   = (tr_df["status"] == "Pending").sum()
            avg_turn    = tr_df["turnaround_days"].dropna().mean() if "turnaround_days" in tr_df.columns else None
            med_turn    = tr_df["turnaround_days"].dropna().median() if "turnaround_days" in tr_df.columns else None
            n_varieties = tr_df["variety"].dropna().nunique() if "variety" in tr_df.columns else 0
            total_def   = tr_df["defect_count"].sum() if "defect_count" in tr_df.columns else 0
            avg_def     = tr_df["defect_count"].mean() if "defect_count" in tr_df.columns else 0

            tk1, tk2, tk3, tk4, tk5 = st.columns(5)
            tk1.markdown(kpi_html("Total Submissions", f"{n_total:,}"), unsafe_allow_html=True)
            tk2.markdown(kpi_html("Completed", f"{n_completed:,}",
                                  f"{n_pending:,} still pending" if n_pending else "All complete"), unsafe_allow_html=True)
            tk3.markdown(kpi_html("Avg Turnaround",
                                  f"{avg_turn:.0f} days" if pd.notna(avg_turn) else "N/A",
                                  f"median {med_turn:.0f} d" if pd.notna(med_turn) else ""), unsafe_allow_html=True)
            tk4.markdown(kpi_html("Varieties Covered", f"{n_varieties:,}"), unsafe_allow_html=True)
            tk5.markdown(kpi_html("Defects Tagged", f"{int(total_def):,}",
                                  f"avg {avg_def:.1f} per submission"), unsafe_allow_html=True)

            st.markdown("---")

            # ── Training velocity over time ───────────────────
            tv_left, tv_right = st.columns([2, 1])
            with tv_left:
                st.markdown('<div class="section-title">Training Velocity</div>', unsafe_allow_html=True)
                st.caption("Submissions per month — how active is the training pipeline?")
                if "date_submit" in tr_df.columns and tr_df["date_submit"].notna().any():
                    tv_df = tr_df.dropna(subset=["date_submit"]).copy()
                    tv_df["month"] = tv_df["date_submit"].dt.to_period("M").astype(str)
                    monthly = tv_df.groupby("month").size().reset_index(name="submissions")
                    fig_tv = px.bar(monthly, x="month", y="submissions",
                                    color_discrete_sequence=[BLUE],
                                    labels={"month":"Month submitted","submissions":"Submissions"})
                    fig_tv.update_traces(hovertemplate="%{x}<br>%{y} submissions<extra></extra>", name="")
                    apply_plot_theme(fig_tv, height=320)
                    fig_tv.update_layout(showlegend=False)
                    st.plotly_chart(fig_tv, use_container_width=True)

            with tv_right:
                st.markdown('<div class="section-title">Status Mix</div>', unsafe_allow_html=True)
                status_counts = tr_df["status"].value_counts().reset_index()
                status_counts.columns = ["Status","Count"]
                fig_st_pie = px.pie(status_counts, names="Status", values="Count",
                                    hole=0.55,
                                    color="Status",
                                    color_discrete_map={"Completed": EMERALD, "Pending": ROSE})
                fig_st_pie.update_traces(textposition="outside", textinfo="label+percent",
                                         hovertemplate="%{label}: %{value} (%{percent})<extra></extra>")
                apply_plot_theme(fig_st_pie, height=320)
                fig_st_pie.update_layout(showlegend=False)
                st.plotly_chart(fig_st_pie, use_container_width=True)

            st.markdown("---")

            # ── Turnaround distribution + by variety ──────────
            tt_left, tt_right = st.columns(2)

            with tt_left:
                st.markdown('<div class="section-title">Turnaround Distribution</div>', unsafe_allow_html=True)
                st.caption("Days from submission to completion. Long tails = bottlenecks worth investigating.")
                if "turnaround_days" in tr_df.columns and tr_df["turnaround_days"].notna().any():
                    fig_tt = px.histogram(tr_df.dropna(subset=["turnaround_days"]),
                                          x="turnaround_days", nbins=20,
                                          color_discrete_sequence=[BLUE],
                                          labels={"turnaround_days":"Turnaround (days)"})
                    fig_tt.update_traces(hovertemplate="%{x:.0f} days: %{y} submissions<extra></extra>", name="")
                    apply_plot_theme(fig_tt, height=320)
                    fig_tt.update_layout(showlegend=False, yaxis_title="Submissions")
                    st.plotly_chart(fig_tt, use_container_width=True)
                else:
                    st.info("No turnaround data available.")

            with tt_right:
                st.markdown('<div class="section-title">Median Turnaround by Variety</div>', unsafe_allow_html=True)
                st.caption("Which varieties are slow to train? Could indicate harder-to-spot defects or low priority.")
                if "turnaround_days" in tr_df.columns and "variety" in tr_df.columns:
                    var_turn = (tr_df.dropna(subset=["turnaround_days","variety"])
                                     .groupby("variety", as_index=False)["turnaround_days"].median()
                                     .sort_values("turnaround_days", ascending=True))
                    if not var_turn.empty:
                        fig_vt = px.bar(var_turn, x="turnaround_days", y="variety", orientation="h",
                                        color="turnaround_days",
                                        color_continuous_scale=["#dbeeff", BLUE],
                                        labels={"turnaround_days":"Median days","variety":"Variety"})
                        fig_vt.update_coloraxes(showscale=False)
                        fig_vt.update_traces(hovertemplate="%{y}: %{x:.0f} days<extra></extra>")
                        apply_plot_theme(fig_vt, height=max(280, len(var_turn)*28))
                        st.plotly_chart(fig_vt, use_container_width=True)

            st.markdown("---")

            # ── Training coverage by variety ──────────────────
            st.markdown('<div class="section-title">Training Coverage by Variety</div>', unsafe_allow_html=True)
            st.caption("How many training submissions per variety, and how many distinct defects each variety has been trained on.")
            if "variety" in tr_df.columns:
                cov = (tr_df.groupby("variety", as_index=False)
                            .agg(submissions=("variety","size"),
                                 unique_defects=("defects_list",
                                                 lambda s: len(set(d for items in s for d in (items or []))))
                                 if "defects_list" in tr_df.columns else ("variety","size"))
                            .sort_values("submissions", ascending=False))

                cf1, cf2 = st.columns(2)
                with cf1:
                    fig_cov = px.bar(cov.sort_values("submissions", ascending=True),
                                     x="submissions", y="variety", orientation="h",
                                     color_discrete_sequence=[BLUE],
                                     labels={"submissions":"# Submissions","variety":"Variety"})
                    fig_cov.update_traces(hovertemplate="%{y}: %{x} submissions<extra></extra>", name="")
                    apply_plot_theme(fig_cov, height=max(300, len(cov)*30))
                    fig_cov.update_layout(showlegend=False)
                    st.plotly_chart(fig_cov, use_container_width=True)
                with cf2:
                    fig_def = px.bar(cov.sort_values("unique_defects", ascending=True),
                                     x="unique_defects", y="variety", orientation="h",
                                     color_discrete_sequence=[NAVY],
                                     labels={"unique_defects":"# Unique Defects Trained","variety":"Variety"})
                    fig_def.update_traces(hovertemplate="%{y}: %{x} unique defects<extra></extra>", name="")
                    apply_plot_theme(fig_def, height=max(300, len(cov)*30))
                    fig_def.update_layout(showlegend=False)
                    st.plotly_chart(fig_def, use_container_width=True)

            st.markdown("---")

            # ── Most-trained defects (overall) ────────────────
            st.markdown('<div class="section-title">Most-Trained Defects</div>', unsafe_allow_html=True)
            st.caption("Across all selected submissions — which defects come up most often? These are your high-priority categories.")
            if "defects_list" in tr_df.columns:
                all_defects = [d for items in tr_df["defects_list"] for d in (items or [])]
                if all_defects:
                    def_counts = pd.Series(all_defects).value_counts().head(15).reset_index()
                    def_counts.columns = ["Defect","Count"]
                    def_counts_asc = def_counts.sort_values("Count", ascending=True)
                    fig_dc = px.bar(def_counts_asc, x="Count", y="Defect", orientation="h",
                                    text="Count",
                                    color_discrete_sequence=[BLUE])
                    fig_dc.update_traces(textposition="outside",
                                         textfont=dict(family="DM Mono, monospace", size=12, color="#0f1d35"),
                                         hovertemplate="%{y}: %{x}<extra></extra>", name="",
                                         cliponaxis=False)
                    apply_plot_theme(fig_dc, height=max(360, 30 * len(def_counts_asc)))
                    fig_dc.update_layout(showlegend=False, xaxis_title=None)
                    fig_dc.update_xaxes(range=[0, def_counts_asc["Count"].max() * 1.15])
                    st.plotly_chart(fig_dc, use_container_width=True)

            st.markdown("---")

            # ── Pending submissions table ─────────────────────
            pending_df = tr_df[tr_df["status"] == "Pending"]
            if not pending_df.empty:
                st.markdown('<div class="section-title">Pending Submissions — Action List</div>', unsafe_allow_html=True)
                st.caption("Training submissions that have not yet been completed. Sort by oldest to find stuck items.")
                today = pd.Timestamp.today().normalize()
                pending_df = pending_df.copy()
                pending_df["days_open"] = (today - pending_df["date_submit"]).dt.days
                cols = [c for c in ["date_submit","variety","reference_dec","decfile_ver","decfile_type","defect_count","days_open","NOTES"] if c in pending_df.columns]
                disp = pending_df[cols].rename(columns={
                    "date_submit":"Submitted","variety":"Variety","reference_dec":"Ref Dec",
                    "decfile_ver":"Version","decfile_type":"Type","defect_count":"# Defects",
                    "days_open":"Days Open","NOTES":"Notes"
                })
                if "Submitted" in disp.columns:
                    disp["Submitted"] = pd.to_datetime(disp["Submitted"]).dt.strftime("%Y-%m-%d")
                disp = disp.sort_values("Days Open", ascending=False)
                st.dataframe(disp, use_container_width=True, hide_index=True, height=320)

            st.markdown("---")

            # ── Cross-link: training → live runs ──────────────
            st.markdown('<div class="section-title">Training → Live Runs Cross-Reference</div>', unsafe_allow_html=True)
            st.caption("Has each trained dec-file version actually been used in production? Versions trained but unused = wasted effort. Versions used heavily = high impact.")
            if "decfile_ver" in tr_df.columns and batches is not None and "decfile_version" in batches.columns:
                ver_counts = (batches["decfile_version"].dropna().astype(str).str.strip()
                                     .value_counts().reset_index())
                ver_counts.columns = ["decfile_ver","batches_used"]
                xref = tr_df.merge(ver_counts, on="decfile_ver", how="left")
                xref["batches_used"] = xref["batches_used"].fillna(0).astype(int)

                trained_total = len(xref)
                trained_used  = (xref["batches_used"] > 0).sum()
                trained_unused = trained_total - trained_used
                pct_used = (trained_used / trained_total * 100) if trained_total else 0

                xc1, xc2 = st.columns([1, 2])
                with xc1:
                    st.markdown(kpi_html("Versions Trained", f"{trained_total:,}"), unsafe_allow_html=True)
                    st.markdown(kpi_html("Used in Production", f"{trained_used:,}",
                                         f"{pct_used:.0f}% of trained"), unsafe_allow_html=True)
                    st.markdown(kpi_html("Unused (yet)", f"{trained_unused:,}"), unsafe_allow_html=True)

                with xc2:
                    top_used = xref[xref["batches_used"] > 0].sort_values("batches_used", ascending=False).head(15)
                    if not top_used.empty:
                        cols = [c for c in ["decfile_ver","variety","date_complete","batches_used","defect_count"] if c in top_used.columns]
                        disp_x = top_used[cols].rename(columns={
                            "decfile_ver":"Version","variety":"Variety","date_complete":"Completed",
                            "batches_used":"Batches Run","defect_count":"# Defects"
                        })
                        if "Completed" in disp_x.columns:
                            disp_x["Completed"] = pd.to_datetime(disp_x["Completed"]).dt.strftime("%Y-%m-%d")
                        st.dataframe(disp_x, use_container_width=True, hide_index=True, height=320)

            st.markdown("---")

            # ── Full record browser ───────────────────────────
            with st.expander("Browse all training records (filtered)"):
                show_cols = [c for c in ["date_submit","date_complete","variety","reference_dec",
                                         "decfile_ver","decfile_type","defect_count","turnaround_days",
                                         "status","NOTES"] if c in tr_df.columns]
                browse = tr_df[show_cols].copy()
                for dc in ("date_submit","date_complete"):
                    if dc in browse.columns:
                        browse[dc] = pd.to_datetime(browse[dc]).dt.strftime("%Y-%m-%d")
                browse = browse.rename(columns={
                    "date_submit":"Submitted","date_complete":"Completed","variety":"Variety",
                    "reference_dec":"Ref","decfile_ver":"Version","decfile_type":"Type",
                    "defect_count":"# Defects","turnaround_days":"Turnaround (d)","status":"Status",
                    "NOTES":"Notes"
                })
                st.dataframe(browse.sort_values("Submitted", ascending=False),
                             use_container_width=True, hide_index=True, height=400)
