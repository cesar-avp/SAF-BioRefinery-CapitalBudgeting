# -*- coding: utf-8 -*-
# %% [markdown]
# # SAF Bio-Refinery | Capital Budgeting & Risk Analysis
# **Version 5.0 — Jupyter Notebook Edition**
#
# *Model for portfolio illustration purposes | Prices: configurable*
#
# ---
# **How to use:**
# - Run cells **in order**, top to bottom, the first time.
# - To change a scenario: edit the inputs in Section 2, 6, or 10,
#   then re-run that cell and every cell below it.
# - All charts are saved automatically as PNG in your working folder.

# %% [markdown]
# ## 0 · Library Installation
# Run this cell only once. If libraries are already installed, it will
# confirm versions without doing anything harmful.

# %%
# ── Install required libraries ────────────────────────────────────────────────
# Run this cell once. Safe to re-run — pip skips already-installed packages.
import subprocess, sys

packages = [
    "yfinance",
    "numpy-financial",
    "scipy",
    "pandas",
    "matplotlib",
    "seaborn",
    ]

for pkg in packages:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", pkg, "-q"]
    )

print("✅ All libraries ready.")

# %% [markdown]
# ## 1 · Imports & Global Chart Style
# Run once. Defines the visual style applied to every chart automatically.

# %%
# ── Standard library ──────────────────────────────────────────────────────────
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")

# ── Data & math ───────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd
import numpy_financial as npf
import yfinance as yf
from scipy.optimize import brentq
from scipy.stats import norm

# ── Visualisation ─────────────────────────────────────────────────────────────
from IPython.display import display
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import matplotlib.patches as mpatches
import seaborn as sns


# In Jupyter: renders charts inline in the notebook
# Uncomment the line below if running in Jupyter (remove the # at the start):
# %matplotlib inline
# In Spyder or script mode, matplotlib renders in a separate window by default.

# ── Global chart style ────────────────────────────────────────────────────────
# One place to change colours / sizes for every chart in the notebook.
C = {
    "bg":     "#fafbfc",   # figure background
    "blue":   "#16213e",   # primary colour (bars, titles, main lines)
    "green":  "#27ae60",   # positive / success
    "red":    "#c0392b",   # negative / risk / loss
    "orange": "#e67e22",   # accent (cumulative lines, warnings)
    "purple": "#8e44ad",   # Monte Carlo histogram
    "gray":   "#666f70",   # secondary text
    "lgray":  "#ecf0f1",   # tornado background
    "navy":   "#1a3a5c",   # strike lines on collar charts
}

TITLE_SIZE  = 12   # Chart titles
LABEL_SIZE  = 10   # Axis labels, tick marks, legend text, annotations
FIG_SIZE    = (10, 5.5)   # Standard figure size (16:9-friendly)
DPI_EXPORT  = 300  # Resolution for saved PNG files


def _style(ax, title="", xlabel="", ylabel=""):
    """
    Apply the corporate visual style to any matplotlib Axes.
    Call at the END of building each chart.
    """
    if title:
        ax.set_title(title, fontsize=TITLE_SIZE, fontweight="bold",
                     color=C["blue"], loc="left", pad=10)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=LABEL_SIZE)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=LABEL_SIZE)
    ax.tick_params(axis="both", labelsize=LABEL_SIZE)
    ax.grid(True, alpha=0.20, linestyle="--", color="#999999")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_facecolor(C["bg"])


def _save(fig, filename):
    """Save chart as PNG (300 DPI) and display it."""
    fig.patch.set_facecolor(C["bg"])
    plt.tight_layout()
    fig.savefig(filename, dpi=DPI_EXPORT, bbox_inches="tight",
                facecolor=C["bg"])
    print(f"  ✔  Saved → {filename}")
    plt.show()


print("✅ Imports and style configuration ready.")

# %% [markdown]
# ---
# ## 2 · INPUT A — Project, Prices & Capital Structure
#
# **Edit the values below to configure your scenario.**
# Every number corresponds to a field from the original GUI.
# Units are shown in the comments on the right.

# %%
# ═══════════════════════════════════════════════════════════════════════════════
# INPUT A — Edit these values for your scenario
# ═══════════════════════════════════════════════════════════════════════════════

# ── Project & Operations ──────────────────────────────────────────────────────
CAPEX_M_USD       = 450       # Capital expenditure (millions USD)
SAF_PRICE_BBL     = 380       # SAF selling price ($/bbl)
UCO_COST_BBL      = 210       # UCO feedstock cost ($/bbl)
OPEX_BBL          = 20        # Operating cost: hydrogen, energy, labour ($/bbl)
CAPACITY_BPD      = 15_000    # Plant capacity (barrels per day)
OPERATING_DAYS    = 310       # Operating days per year (allows for maintenance)
PROJECT_LIFE      = 15        # Project evaluation horizon (years)
TAX_RATE_PCT      = 25        # Corporate tax rate (%)
NWC_PCT_REVENUE   = 7         # Net Working Capital as % of annual revenue (%)
DEPRECIATION      = "Straight-Line"   # "Straight-Line"  or  "MACRS"

# ── Capital Structure & WACC ──────────────────────────────────────────────────
PROXY_TICKER      = "VLO"     # Yahoo Finance ticker for beta proxy company
KD_PRETAX_PCT     = 14        # Pre-tax cost of debt (%)
WEIGHT_EQUITY_PCT = 60        # Equity weight in capital structure (%)
WEIGHT_DEBT_PCT   = 40        # Debt weight in capital structure (%)
MANUAL_WACC_PCT   = None      # Set a number to override CAPM (e.g. 9.5)
                              # Leave as None to calculate from market data
AMORTIZATION      = "Linear"  # "Linear" (equal annual) or "Bullet" (lump-sum)

# ── Convert inputs to model-ready format (do not edit below this line) ────────
A = {
    "capex_usd":           CAPEX_M_USD * 1_000_000,
    "saf_price_per_bbl":   SAF_PRICE_BBL,
    "uco_cost_per_bbl":    UCO_COST_BBL,
    "opex_per_bbl":        OPEX_BBL,
    "capacity_bpd":        CAPACITY_BPD,
    "operating_days":      OPERATING_DAYS,
    "project_life_years":  PROJECT_LIFE,
    "tax_rate":            TAX_RATE_PCT / 100,
    "nwc_pct":             NWC_PCT_REVENUE / 100,
    "depr_method":         DEPRECIATION,
    "ticker":              PROXY_TICKER.upper(),
    "kd_pretax":           KD_PRETAX_PCT / 100,
    "weight_equity":       WEIGHT_EQUITY_PCT / 100,
    "weight_debt":         WEIGHT_DEBT_PCT / 100,
    "wacc_manual":         MANUAL_WACC_PCT / 100 if MANUAL_WACC_PCT else None,
    "amort_method":        AMORTIZATION,
}

print("✅ Input Group A loaded.")
print(f"   CAPEX: ${A['capex_usd']/1e6:.0f}M  |  "
      f"SAF: ${A['saf_price_per_bbl']}/bbl  |  "
      f"UCO: ${A['uco_cost_per_bbl']}/bbl  |  "
      f"OPEX: ${A['opex_per_bbl']}/bbl")
print(f"   Capacity: {A['capacity_bpd']:,} bpd  |  "
      f"Op. Days: {A['operating_days']}  |  "
      f"Life: {A['project_life_years']} yrs  |  "
      f"Tax: {A['tax_rate']*100:.0f}%")

# %% [markdown]
# ## 3 · Macroeconomic Data & WACC Calculation

# %%
# ── Fetch market data from Yahoo Finance ──────────────────────────────────────
print("Fetching market data from Yahoo Finance...")
print("-" * 45)

# Beta from proxy company
try:
    info = yf.Ticker(A["ticker"]).info
    raw_beta = info.get("beta")
    # In newer yfinance versions, .info values can be wrapped — force scalar
    beta = float(raw_beta) if raw_beta is not None else 1.10
    if np.isnan(beta):
        beta = 1.10
    print(f"  ✔ Beta ({A['ticker']}): {beta:.2f}x")
except Exception as e:
    beta = 1.10
    print(f"  ⚠ Beta unavailable ({e}) → fallback: {beta}x")

# Risk-Free Rate: 10-year US Treasury yield
# Fix: use .history() instead of yf.download() to avoid MultiIndex NaN bug
try:
    tnx       = yf.Ticker("^TNX").history(period="5d")
    tnx_close = tnx["Close"].dropna()
    if len(tnx_close) < 1:
        raise ValueError("Empty series returned.")
    rf = float(tnx_close.iloc[-1]) / 100   # ^TNX is already in percentage
    if np.isnan(rf):
        raise ValueError("NaN value returned.")
    print(f"  ✔ Risk-Free Rate (10Y Treasury): {rf*100:.2f}%")
except Exception as e:
    rf = 0.045
    print(f"  ⚠ ^TNX unavailable ({e}) → fallback Rf: {rf*100:.1f}%")

# Market Return: S&P 500 geometric CAGR over 10 years
if A["wacc_manual"] is None:
    try:
        sp500       = yf.Ticker("^GSPC").history(period="10y")
        sp500_close = sp500["Close"].dropna()
        if len(sp500_close) < 2:
            raise ValueError("Insufficient price history.")
        sv = float(sp500_close.iloc[0])
        ev = float(sp500_close.iloc[-1])
        if np.isnan(sv) or np.isnan(ev):
            raise ValueError("NaN in price series.")
        rm = (ev / sv) ** (1 / 10) - 1
        print(f"  ✔ S&P 500 CAGR (10Y): {rm*100:.2f}%")
    except Exception as e:
        rm = 0.105
        print(f"  ⚠ ^GSPC unavailable ({e}) → fallback Rm: {rm*100:.1f}%")
else:
    rm = None
    print(f"  ℹ Manual WACC set — CAPM skipped.")

# ── WACC Calculation ──────────────────────────────────────────────────────────
kd_net = A["kd_pretax"] * (1 - A["tax_rate"])  # After-tax cost of debt

if A["wacc_manual"] is not None:
    wacc = A["wacc_manual"]
    ke   = None
else:
    # CAPM: Ke = Rf + Beta × (Rm − Rf)
    ke   = rf + beta * (rm - rf)
    # WACC = We × Ke + Wd × Kd_net
    wacc = A["weight_equity"] * ke + A["weight_debt"] * kd_net

# Store macro results for downstream use
MACRO = {"ticker": A["ticker"], "beta": beta,
         "risk_free_rate": rf, "market_return": rm}
WACC_DATA = {"wacc": wacc, "ke": ke,
             "kd_after_tax": kd_net, "kd_pretax": A["kd_pretax"]}

# ── WACC Summary Table ────────────────────────────────────────────────────────
print("\n" + "─" * 45)
wacc_rows = {
    "Proxy Company (Beta Source)":  f"{A['ticker']}  |  β = {beta:.2f}x",
    "Risk-Free Rate (Rf)":          f"{rf*100:.2f}%  (10Y US Treasury)",
    "Market Return (Rm)":           f"{rm*100:.2f}%  (S&P 500 10Y CAGR)" if rm else "N/A (Manual WACC)",
    "Equity Risk Premium (Rm−Rf)":  f"{(rm-rf)*100:.2f}%" if rm else "N/A",
    "Cost of Equity Ke (CAPM)":     f"{ke*100:.2f}%" if ke else "Manual override",
    "Pre-Tax Cost of Debt (Kd)":    f"{A['kd_pretax']*100:.1f}%",
    "Tax Shield  →  Kd After-Tax":  f"{kd_net*100:.2f}%",
    "Capital Structure":            f"Equity {A['weight_equity']*100:.0f}%  /  Debt {A['weight_debt']*100:.0f}%",
    "WACC (Hurdle Rate)":           f"{wacc*100:.2f}%  ◄",
}
wacc_df = pd.DataFrame(wacc_rows.items(), columns=["Parameter", "Value"])
wacc_df = wacc_df.set_index("Parameter")
display(wacc_df.style
        .set_properties(**{"font-size": "11px", "text-align": "left"})
        .set_table_styles([{"selector": "th",
                            "props": [("font-size", "11px"),
                                      ("font-weight", "bold"),
                                      ("background-color", "#eaf0fb")]}])
       )

# %% [markdown]
# ## 4 · Financial Model — FCF, DSCR & KPIs

# %%
# ── Depreciation schedule ─────────────────────────────────────────────────────
N    = A["project_life_years"]
capex = A["capex_usd"]
tax   = A["tax_rate"]

if A["depr_method"] == "MACRS" and N == 15:
    # IRS Publication 946 — 15-year property, Half-Year Convention
    depr_sched = capex * np.array([
        0.0500, 0.0950, 0.0855, 0.0770, 0.0693, 0.0623,
        0.0590, 0.0590, 0.0591, 0.0590, 0.0591, 0.0590,
        0.0591, 0.0590, 0.0591
    ])
else:
    depr_sched = np.full(N, capex / N)   # Straight-Line

avg_depr    = depr_sched.mean()
ann_vol     = A["capacity_bpd"] * A["operating_days"]   # Annual barrels
ann_factor  = (1 - (1 + wacc) ** (-N)) / wacc           # Annuity factor

# ── Build P&L DataFrame ───────────────────────────────────────────────────────
years = np.arange(0, N + 1)
df = pd.DataFrame(0.0, index=years,
                  columns=["Revenues", "COGS_UCO", "OPEX", "EBITDA",
                            "Depreciation", "EBIT", "Taxes", "NOPAT",
                            "NWC", "Delta_NWC", "CAPEX", "FCF",
                            "Cumulative_FCF", "Debt_Balance",
                            "Interest_Expense", "Principal_Payment",
                            "Debt_Service", "DSCR"])
df.index.name = "Year"

op = slice(1, N + 1)   # Vectorised slice for operating years

df.loc[op, "Revenues"] = ann_vol * A["saf_price_per_bbl"]
df.loc[op, "COGS_UCO"] = ann_vol * A["uco_cost_per_bbl"]
df.loc[op, "OPEX"]     = ann_vol * A["opex_per_bbl"]
df.loc[op, "EBITDA"]   = (df.loc[op, "Revenues"]
                          - df.loc[op, "COGS_UCO"]
                          - df.loc[op, "OPEX"])
df.loc[1:N, "Depreciation"] = depr_sched
df["EBIT"]   = df["EBITDA"] - df["Depreciation"]
df["Taxes"]  = np.where(df["EBIT"] > 0, df["EBIT"] * tax, 0.0)
df["NOPAT"]  = df["EBIT"] - df["Taxes"]

# NWC: build-up Year 1, flat Years 2..N-1, full recovery Year N
df.loc[op, "NWC"]   = df.loc[op, "Revenues"] * A["nwc_pct"]
df["Delta_NWC"]     = df["NWC"].diff().fillna(0.0)
df.loc[N, "Delta_NWC"] = -df.loc[N, "NWC"]   # terminal NWC recovery

df.loc[0, "CAPEX"] = capex
df["FCF"]          = df["NOPAT"] + df["Depreciation"] - df["CAPEX"] - df["Delta_NWC"]
df["Cumulative_FCF"] = df["FCF"].cumsum()

# ── Debt schedule ─────────────────────────────────────────────────────────────
debt = capex * A["weight_debt"]
yr   = np.arange(1, N + 1)

if A["amort_method"] == "Linear":
    ann_principal = debt / N
    df.loc[1:, "Debt_Balance"]      = np.maximum(debt - ann_principal * (yr - 1), 0)
    df.loc[1:, "Principal_Payment"] = ann_principal
else:   # Bullet
    df.loc[1:,  "Debt_Balance"]     = debt
    df.loc[N,   "Debt_Balance"]     = 0.0
    df.loc[1:,  "Principal_Payment"]= 0.0
    df.loc[N,   "Principal_Payment"]= debt

df.loc[1:, "Interest_Expense"] = df.loc[1:, "Debt_Balance"] * A["kd_pretax"]
df.loc[1:, "Debt_Service"]     = (df.loc[1:, "Interest_Expense"]
                                  + df.loc[1:, "Principal_Payment"])
ds_safe = df.loc[1:, "Debt_Service"].replace(0, np.nan)
df.loc[1:, "DSCR"] = df.loc[1:, "EBITDA"] / ds_safe

# ── Capital Budgeting KPIs ────────────────────────────────────────────────────
npv_val = npf.npv(wacc, df["FCF"].values)

try:
    irr_val = float(npf.irr(df["FCF"].values))
    irr_val = None if np.isnan(irr_val) else irr_val
except Exception:
    irr_val = None

neg = df["Cumulative_FCF"] < 0
if not neg.any():
    payback = 0.0
elif neg.all():
    payback = float("inf")
else:
    ln = df[neg].index[-1]
    payback = float(ln + abs(df.loc[ln, "Cumulative_FCF"]) / df.loc[ln+1, "FCF"])

# Break-even SAF price (minimum price for NPV = 0)
def _npv_at_saf(saf_p):
    eb = ann_vol * (saf_p - A["uco_cost_per_bbl"] - A["opex_per_bbl"])
    ei = eb - avg_depr
    n  = ei - max(0.0, ei * tax)
    return -capex + (n + avg_depr) * ann_factor

try:
    breakeven_saf = brentq(_npv_at_saf, 50, 600, xtol=0.01)
except ValueError:
    breakeven_saf = float("nan")

# Store for summary table
FCF_DATA = {
    "df": df, "npv": npv_val, "irr": irr_val,
    "payback": payback, "breakeven_saf": breakeven_saf,
    "annual_volume": ann_vol, "avg_depreciation": avg_depr,
    "annuity_factor": ann_factor, "debt_amount": debt,
}

# ── FCF Table (Years 0–5 preview) ─────────────────────────────────────────────
fmt_m = lambda x: f"${x/1e6:,.1f}M"
preview_cols = ["Revenues", "COGS_UCO", "OPEX", "EBITDA",
                "Depreciation", "EBIT", "Taxes", "NOPAT",
                "FCF", "Cumulative_FCF"]
preview = df[preview_cols].head(6).copy()
for col in preview_cols:
    preview[col] = preview[col].apply(fmt_m)

print("P&L Preview — Years 0 to 5  (values in M USD)")
display(preview.style
        .set_properties(**{"font-size": "10px", "text-align": "right"})
        .set_table_styles([{"selector": "th",
                            "props": [("font-size", "10px"),
                                      ("font-weight", "bold"),
                                      ("background-color", "#eaf0fb")]}])
       )

irr_str = f"{irr_val*100:.2f}%" if irr_val else "N/A"
print(f"\nNPV @ {wacc*100:.2f}% WACC : ${npv_val/1e6:,.1f}M")
print(f"IRR                     : {irr_str}")
print(f"Payback Period          : {payback:.2f} years")
print(f"Break-Even SAF Price    : ${breakeven_saf:.1f}/bbl")
print(f"Min DSCR                : {df.loc[1:,'DSCR'].min():.2f}x  "
      f"({'✔ OK' if df.loc[1:,'DSCR'].min() >= 1.20 else '✘ COVENANT BREACH'})")

# %% [markdown]
# ## 5 · Chart 1 — J-Curve: Annual & Cumulative FCF

# %%
fig, ax_l = plt.subplots(figsize=FIG_SIZE)

bar_c = [C["red"] if y == 0 else C["blue"] for y in df.index]
ax_l.bar(df.index, df["FCF"] / 1e6, color=bar_c, alpha=0.82,
         zorder=2, label="Annual FCF")

ax_r = ax_l.twinx()
ax_r.plot(df.index, df["Cumulative_FCF"] / 1e6,
          color=C["orange"], marker="o", markersize=4.5,
          linewidth=2.5, zorder=3, label="Cumulative FCF")
ax_r.set_ylabel("Cumulative FCF (M USD)", fontsize=LABEL_SIZE)
ax_r.tick_params(labelsize=LABEL_SIZE)
ax_r.yaxis.set_major_formatter(tkr.StrMethodFormatter("{x:,.0f}"))
ax_r.spines["top"].set_visible(False)
ax_r.spines["right"].set_visible(False)
ax_r.grid(False)

ax_l.axhline(0, color="black", linewidth=0.9, linestyle="--")
ax_l.axvline(payback, color=C["green"], linewidth=2.0, linestyle="--",
             zorder=3, label=f"Payback: {payback:.2f} yrs")
ax_l.set_xticks(df.index)
ax_l.yaxis.set_major_formatter(tkr.StrMethodFormatter("{x:,.0f}"))

# KPI annotation box
irr_lbl = f"{irr_val*100:.1f}%" if irr_val else "N/A"
ax_l.text(
    0.7875, 0.305,
        f"NPV: ${npv_val/1e6:,.0f}M\n"
        f"IRR: {irr_lbl}\n"
        f"Break-Even: ${breakeven_saf:.0f}/bbl",
    transform=ax_l.transAxes, ha="left", va="top", fontsize=LABEL_SIZE,
    color="black",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
              alpha=0.80, edgecolor="#cccccc")
    )

# Legend above the chart (outside plot area)
h1, l1 = ax_l.get_legend_handles_labels()
h2, l2 = ax_r.get_legend_handles_labels()

ax_l.legend(h1 + h2, l1 + l2, fontsize=LABEL_SIZE, ncol=1,
            loc="upper left", bbox_to_anchor=(0.775, 0.19),
            frameon=True, framealpha=0.8, edgecolor="#cccccc")

_style(ax_l,
       title="",
       xlabel="Project Year",
       ylabel="Annual FCF (M USD)")

# Forzamos al título a separarse de la gráfica para hacerle hueco a la leyenda
ax_l.set_title("J-Curve — Annual & Cumulative Free Cash Flow", pad=10, 
               fontsize=TITLE_SIZE, fontweight="bold", color=C["blue"])

_save(fig, "1_J_Curve.png")

# %% [markdown]
# ---
# ## 6 · INPUT B — Risk & Monte Carlo Parameters
#
# Edit these values before running the risk analysis cells below.

# %%
# ═══════════════════════════════════════════════════════════════════════════════
# INPUT B — Risk & Monte Carlo  (edit values here)
# ═══════════════════════════════════════════════════════════════════════════════

N_SIMULATIONS     = 10_000  # Number of Monte Carlo scenarios

# Volatilities: percentage of the base value (σ as % of the mean)
SIGMA_SAF_PCT     = 40   # SAF price volatility  (%)
SIGMA_UCO_PCT     = 30   # UCO cost volatility   (%)
SIGMA_OPEX_PCT    = 18   # OPEX volatility       (%)
SIGMA_DAYS_PCT    = 10    # Operating days volatility (%)
SIGMA_CAPEX_PCT   = 15   # CAPEX overrun range   (%)
SIGMA_WACC_BPS    = 250  # WACC uncertainty      (basis points)

# ── Convert to model-ready format ─────────────────────────────────────────────
B = {
    "n_sims":      N_SIMULATIONS,
    "sigma_saf":   SIGMA_SAF_PCT   / 100,
    "sigma_uco":   SIGMA_UCO_PCT   / 100,
    "sigma_opex":  SIGMA_OPEX_PCT  / 100,
    "sigma_days":  SIGMA_DAYS_PCT  / 100,
    "sigma_capex": SIGMA_CAPEX_PCT / 100,
    "sigma_wacc":  SIGMA_WACC_BPS  / 10_000,
}

print("✅ Input Group B loaded.")
print(f"   Simulations: {N_SIMULATIONS:,}  |  "
      f"σ SAF: {SIGMA_SAF_PCT}%  |  σ UCO: {SIGMA_UCO_PCT}%  |  "
      f"σ CAPEX: {SIGMA_CAPEX_PCT}%  |  σ WACC: {SIGMA_WACC_BPS} bps")

# %% [markdown]
# ## 7 · Chart 2 — NPV Sensitivity Heatmap (SAF vs UCO)

# %%

# Heatmap range: dynamic around base prices from INPUT A

HEATMAP_STRESS = 0.40  # 40% stress coverage
HEATMAP_STEPS = 7  # Must be an odd number (e.g., 5, 7, 9) to have a center

saf_base_hm = A["saf_price_per_bbl"]
uco_base_hm = A["uco_cost_per_bbl"]

# Vectorised grid calculation using np.meshgrid (no loops)
saf_range = np.linspace(saf_base_hm * (1 - HEATMAP_STRESS),
                         saf_base_hm * (1 + HEATMAP_STRESS),
                         HEATMAP_STEPS).round(0).astype(int)

uco_range = np.linspace(uco_base_hm * (1 - HEATMAP_STRESS),
                        uco_base_hm * (1 + HEATMAP_STRESS),
                        HEATMAP_STEPS).round(0).astype(int)

SAF_G, UCO_G = np.meshgrid(saf_range, uco_range)

rev_g    = ann_vol * SAF_G
cogs_g   = ann_vol * UCO_G
ebitda_g = rev_g - cogs_g - ann_vol * A["opex_per_bbl"]
ebit_g   = ebitda_g - avg_depr
fcf_g    = (ebit_g - np.where(ebit_g > 0, ebit_g * tax, 0.0)) + avg_depr
npv_g    = (-capex + fcf_g * ann_factor) / 1e6

sens_matrix = pd.DataFrame(npv_g, index=uco_range, columns=saf_range)
sens_matrix.index.name   = "UCO_Cost"
sens_matrix.columns.name = "SAF_Price"

fig, ax = plt.subplots(figsize=FIG_SIZE)

sns.heatmap(
    sens_matrix, annot=True, fmt=".0f",
    cmap=sns.diverging_palette(10, 130, as_cmap=True),
    center=0,
    cbar_kws={"label": "NPV (M USD)", "shrink": 0.85},
    ax=ax, linewidths=0.4,
    annot_kws={"size": LABEL_SIZE}
)
ax.invert_yaxis()
ax.tick_params(axis="both", labelsize=LABEL_SIZE)
ax.grid(False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_title("NPV Sensitivity: SAF Price vs UCO Cost  (M USD)",
             fontsize=TITLE_SIZE, fontweight="bold",
             color=C["blue"], loc="center", pad=10)
ax.set_xlabel("SAF Selling Price ($/bbl)", fontsize=LABEL_SIZE)
ax.set_ylabel("UCO Feedstock Cost ($/bbl)", fontsize=LABEL_SIZE)

_save(fig, "2_Sensitivity_Heatmap.png")

# %% [markdown]
# ## 8 · Chart 3 — Monte Carlo NPV Distribution

# %%
np.random.seed(42)   # Fixed seed → reproducible results every run

N_s = B["n_sims"]
saf_base = A["saf_price_per_bbl"]
uco_base = A["uco_cost_per_bbl"]

# Log-normal for prices (prices cannot be negative; mean preserved exactly)
mu_saf = np.log(saf_base) - 0.5 * B["sigma_saf"] ** 2
mu_uco = np.log(uco_base) - 0.5 * B["sigma_uco"] ** 2
mc_saf  = np.random.lognormal(mu_saf, B["sigma_saf"], N_s)
mc_uco  = np.random.lognormal(mu_uco, B["sigma_uco"], N_s)

# Normal distribution for operational variables
mc_opex = np.random.normal(A["opex_per_bbl"],
                            A["opex_per_bbl"] * B["sigma_opex"], N_s)
mc_days = np.random.normal(A["operating_days"],
                            A["operating_days"] * B["sigma_days"], N_s
                           ).clip(150, 365)
mc_capex_s = np.random.normal(capex, capex * B["sigma_capex"], N_s
                               ).clip(capex * 0.70, capex * 1.50)
mc_wacc_s  = np.random.normal(wacc, B["sigma_wacc"], N_s).clip(0.03, 0.35)

mc_vol    = A["capacity_bpd"] * mc_days
mc_ebitda = mc_vol * mc_saf - mc_vol * mc_uco - mc_vol * mc_opex
mc_ebit   = mc_ebitda - mc_capex_s / N
mc_nopat  = mc_ebit - np.where(mc_ebit > 0, mc_ebit * tax, 0.0)
mc_fcf    = mc_nopat + mc_capex_s / N
mc_af     = (1 - (1 + mc_wacc_s) ** (-N)) / mc_wacc_s
mc_npv    = -mc_capex_s + mc_fcf * mc_af

# Risk KPIs
mean_npv     = mc_npv.mean()
prob_success = (mc_npv > 0).mean() * 100
var5         = float(np.percentile(mc_npv, 5))
var10        = float(np.percentile(mc_npv, 10))

# Fan chart data (built here, used in Chart 7)
capex_row   = (-mc_capex_s).reshape(1, N_s)
fcf_tile    = np.tile(mc_fcf, (N, 1))
cum_mat     = np.cumsum(np.vstack([capex_row, fcf_tile]), axis=0) / 1e6
fan_data = pd.DataFrame(
    np.percentile(cum_mat, [10, 25, 50, 75, 90], axis=1).T,
    columns=["P10", "P25", "P50", "P75", "P90"],
    index=np.arange(0, N + 1)
)
fan_data.index.name = "Year"

RISK_DATA = {
    "mean_npv": mean_npv, "prob_success": prob_success,
    "var_5": var5, "var_10": var10,
    "mc_npv": mc_npv,
    "sens_matrix": sens_matrix,
    "fan_data": fan_data,
    "base_npv": npv_val,
}

# ── Plot ──────────────────────────────────────────────────────────────────────
npv_m = mc_npv / 1e6
var5_m = var5 / 1e6

fig, ax = plt.subplots(figsize=FIG_SIZE)

sns.histplot(npv_m, bins='auto', kde=True,
             color=C["purple"], alpha=0.45, ax=ax, zorder=2)

# VaR tail shading (enhanced with ax.vspan)
#x_shade = np.linspace(float(npv_m.min()), var5_m, 400)
#ax.fill_between(x_shade, 0, ax.get_ylim()[1] * 50,
#                alpha=0.22, color=C["red"], zorder=1,
#                label=f"VaR(5%) Region  <  ${var5_m:,.0f}M")

ax.axvspan(float(npv_m.min()), var5_m,
           alpha=0.22, color=C["red"], zorder=1,
           label=f"VaR(5%) Region  <  ${var5_m:,.0f}M")

ax.axvline(0, color=C["red"], linewidth=2.2, linestyle="-",
           label="Break-even  (NPV = 0)")
ax.axvline(mean_npv / 1e6, color=C["green"], linewidth=2.0,
           linestyle="--", label=f"Mean NPV: ${mean_npv/1e6:,.0f}M")
ax.axvline(var5_m, color=C["orange"], linewidth=1.8,
           linestyle=":", label=f"VaR(5%): ${var5_m:,.0f}M")

ax.text(0.764, 0.965, f"P(NPV > 0): {prob_success:.1f}%",
        transform=ax.transAxes, ha="left", va="top",
        fontsize=LABEL_SIZE, color=C["green"], fontweight="bold", 
        bbox=dict(facecolor='white', alpha=0.8, edgecolor="#cccccc"))

ax.xaxis.set_major_formatter(tkr.StrMethodFormatter("{x:,.0f}"))

ax.legend(fontsize=LABEL_SIZE, ncol=1,
          loc="upper left", bbox_to_anchor=(0.75, 0.92),
          frameon=True, framealpha=0.8, edgecolor="#cccccc")

_style(ax,
       title="",  # The string keeps without text to avoid overlap a personalized title 
       xlabel="NPV (M USD)", ylabel="Frequency",)

# Forzamos al título a separarse de la gráfica para hacerle hueco a la leyenda
ax.set_title(f"Monte Carlo NPV Distribution ({N_s:,} scenarios, 6 variables)", pad=10, 
               fontsize=TITLE_SIZE, fontweight="bold", color=C["blue"], loc="center")

_save(fig, "3_Monte_Carlo.png")

print(f"\nMean NPV     : ${mean_npv/1e6:,.1f}M")
print(f"P(NPV > 0)   : {prob_success:.1f}%")
print(f"VaR (5%)     : ${var5/1e6:,.1f}M")
print(f"VaR (10%)    : ${var10/1e6:,.1f}M")

# %% [markdown]
# ## 9 · Chart 4 — Tornado Chart (OAT ±10%)

# %%
SHOCK = 0.10   # 10% stress applied one variable at a time

def _qnpv(saf_p, uco_p, opex_p, vol_p, capex_p, wacc_p):
    """Simplified NPV for tornado OAT calculations only."""
    eb = vol_p * (saf_p - uco_p - opex_p)
    ei = eb - capex_p / N
    np_ = ei - max(0.0, ei * tax)
    af_ = (1 - (1 + wacc_p) ** (-N)) / wacc_p
    return -capex_p + (np_ + capex_p / N) * af_

base_args = (saf_base, uco_base, A["opex_per_bbl"],
             ann_vol, capex, wacc)
tornado_vars = [
    ("SAF Price", 0), ("UCO Cost", 1), ("OPEX/bbl", 2),
    ("Op. Days",  3), ("CAPEX",    4), ("WACC",     5),
]

rows = []
for vname, idx in tornado_vars:
    up   = list(base_args); up[idx]   *= (1 + SHOCK)
    down = list(base_args); down[idx] *= (1 - SHOCK)
    hi = max(_qnpv(*up), _qnpv(*down)) / 1e6
    lo = min(_qnpv(*up), _qnpv(*down)) / 1e6
    rows.append({"Variable": vname, "NPV_High": hi,
                 "NPV_Low": lo, "Range": hi - lo})

df_torn = pd.DataFrame(rows).sort_values("Range", ascending=True)

# ── Plot ──────────────────────────────────────────────────────────────────────
base_m = npv_val / 1e6
fig, ax = plt.subplots(figsize=(11, 5.5))

min_npv = df_torn["NPV_Low"].min()
max_npv = df_torn["NPV_High"].max()
margin_x = (max_npv - min_npv) * 0.10
ax.set_xlim(min_npv - margin_x, max_npv + margin_x)

for i, (_, row) in enumerate(df_torn.iterrows()):
    ax.barh(i, row["NPV_High"] - base_m, left=base_m,
            color=C["green"], alpha=0.80, height=0.55)
    ax.barh(i, row["NPV_Low"]  - base_m, left=base_m,
            color=C["red"],   alpha=0.80, height=0.55)

    ax.text(row["NPV_High"], i + 0.35,
            f"${row['NPV_High']:,.0f}M",
            va="center", ha="left", fontsize=LABEL_SIZE,
            color=C["green"], fontweight="bold")
    
    ax.text(row["NPV_Low"], i + 0.35,
            f"${row['NPV_Low']:,.0f}M",
            va="center", ha="right", fontsize=LABEL_SIZE,
            color=C["red"], fontweight="bold")


    # Δ Range label — axes fraction coordinates → never clipped
    frac_y = (i + 0.5) / max(len(df_torn), 1)
    ax.annotate(
        f"  Δ ${row['Range']:,.0f}M",
        xy=(1.0, frac_y),
        xycoords=("axes fraction", "axes fraction"),
        ha="left", va="center", fontsize=LABEL_SIZE,
        color=C["gray"], style="italic",
        annotation_clip=False
    )

ax.set_yticks(range(len(df_torn)))
ax.set_yticklabels(df_torn["Variable"], fontsize=LABEL_SIZE)
ax.axvline(base_m, color="black", linewidth=1.4, linestyle="--",
           label=f"NPV Base: ${base_m:,.0f}M")
ax.xaxis.set_major_formatter(tkr.StrMethodFormatter("{x:,.0f}"))
ax.set_facecolor(C["lgray"])

ax.legend(fontsize=LABEL_SIZE,
          loc="upper left", bbox_to_anchor=(0.775, 0.1),
          frameon=True, framealpha=0.9, edgecolor="#cccccc")

_style(ax,
       title="",
       xlabel="NPV (M USD)", ylabel="")

# Forzamos al título a separarse de la gráfica y centrarse
ax.set_title("Tornado Chart — OAT ±10% Sensitivity on NPV", pad=10, 
               fontsize=TITLE_SIZE, fontweight="bold", color=C["blue"], loc="center")

plt.subplots_adjust(right=0.84)   # room for Δ labels
_save(fig, "4_Tornado_Chart.png")

# %% [markdown]
# ---
# ## 10 · INPUT C — Collar Strike Prices
#
# Edit these values to define the hedging strategy.
# Floor = minimum price guaranteed.  Cap = maximum price subject to.

# %%
# ═══════════════════════════════════════════════════════════════════════════════
# INPUT C — Collar Parameters  (edit values here)
# ═══════════════════════════════════════════════════════════════════════════════

# UCO Leg — Raw Material Side (protect against rising costs)
UCO_FLOOR_BBL     = 168    # Put strike: maximum effective UCO cost ($/bbl)
UCO_CAP_BBL       = 252   # Call strike: minimum UCO price to benefit from ($/bbl)
UCO_VOLATILITY_PCT= 30    # Annualised UCO price volatility (%)

# SAF Leg — Product Side (protect against falling revenues)
SAF_FLOOR_BBL     = 329   # Put strike: minimum effective SAF price ($/bbl)
SAF_CAP_BBL       = 430   # Call strike: maximum SAF price to benefit from ($/bbl)
SAF_VOLATILITY_PCT= 38    # Annualised SAF price volatility (%)

OPTION_TERM_YRS   = 1     # Option expiry (years)

# ── Convert ───────────────────────────────────────────────────────────────────
C_inp = {
    "uco_floor": UCO_FLOOR_BBL,  "uco_cap":  UCO_CAP_BBL,
    "vol_uco":   UCO_VOLATILITY_PCT / 100,
    "saf_floor": SAF_FLOOR_BBL,  "saf_cap":  SAF_CAP_BBL,
    "vol_saf":   SAF_VOLATILITY_PCT / 100,
    "T_option":  OPTION_TERM_YRS,
}

print("✅ Input Group C loaded.")
print(f"   UCO Collar: Put @ ${UCO_FLOOR_BBL}/bbl  |  Call @ ${UCO_CAP_BBL}/bbl  "
      f"|  σ = {UCO_VOLATILITY_PCT}%")
print(f"   SAF Collar: Put @ ${SAF_FLOOR_BBL}/bbl  |  Call @ ${SAF_CAP_BBL}/bbl  "
      f"|  σ = {SAF_VOLATILITY_PCT}%")

# ── Reference check (no editar) ───────────────────────────────────────────────
# Suggested strikes based on 1σ volatility anchored to current base prices
saf_floor_ref = round(A["saf_price_per_bbl"] * (1 - SAF_VOLATILITY_PCT/100))
saf_cap_ref   = round(A["saf_price_per_bbl"] * (1 + SAF_VOLATILITY_PCT/100))
uco_floor_ref = round(A["uco_cost_per_bbl"]  * (1 - UCO_VOLATILITY_PCT/100))
uco_cap_ref   = round(A["uco_cost_per_bbl"]  * (1 + UCO_VOLATILITY_PCT/100))

print("── Your strikes vs. 1σ reference ───────────────────────")
print(f"  UCO Floor: ${UCO_FLOOR_BBL}/bbl  (reference: ${uco_floor_ref})")
print(f"  UCO Cap:   ${UCO_CAP_BBL}/bbl  (reference: ${uco_cap_ref})")
print(f"  SAF Floor: ${SAF_FLOOR_BBL}/bbl  (reference: ${saf_floor_ref})")
print(f"  SAF Cap:   ${SAF_CAP_BBL}/bbl  (reference: ${saf_cap_ref})")
print(f"\n  Net Collar Cost will be calculated after Black-Scholes.")
print(f"  Target: |net_cost_bbl| < $2.00 for Zero-Cost structure.")

# %% [markdown]
# ## 11 · Collar Valuation (Black-Scholes)

# %%
def _bs(S, K, T, r, sigma, opt="call"):
    """
    Black-Scholes European option pricing.
    S=spot, K=strike, T=term(yrs), r=risk-free, sigma=volatility, opt=call/put.
    """
    S  = np.maximum(np.asarray(S, float), 1e-6)
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if opt == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

rf   = MACRO["risk_free_rate"]
T_op = C_inp["T_option"]

# Four option premiums
put_uco  = float(_bs(A["uco_cost_per_bbl"],   C_inp["uco_floor"], T_op, rf, C_inp["vol_uco"],  "put"))
call_uco = float(_bs(A["uco_cost_per_bbl"],   C_inp["uco_cap"],   T_op, rf, C_inp["vol_uco"],  "call"))
put_saf  = float(_bs(A["saf_price_per_bbl"],  C_inp["saf_floor"], T_op, rf, C_inp["vol_saf"],  "put"))
call_saf = float(_bs(A["saf_price_per_bbl"],  C_inp["saf_cap"],   T_op, rf, C_inp["vol_saf"],  "call"))

net_cost_bbl   = (put_uco - call_uco) + (put_saf - call_saf)
net_cost_annual = net_cost_bbl * ann_vol

# Payoff data for charts
uco_x   = np.linspace(C_inp["uco_floor"] * 0.50,  C_inp["uco_cap"] * 1.25, 600)
saf_x   = np.linspace(C_inp["saf_floor"] * 0.50,  C_inp["saf_cap"] * 1.25, 600)
opex    = A["opex_per_bbl"]

mg_nh_uco  = A["saf_price_per_bbl"] - uco_x - opex
mg_col_uco = A["saf_price_per_bbl"] - np.clip(uco_x, C_inp["uco_floor"], C_inp["uco_cap"]) - opex
mg_put_uco = mg_nh_uco + np.maximum(C_inp["uco_floor"] - uco_x, 0)

mg_nh_saf  = saf_x - A["uco_cost_per_bbl"] - opex
mg_col_saf = np.clip(saf_x, C_inp["saf_floor"], C_inp["saf_cap"]) - A["uco_cost_per_bbl"] - opex

HEDGE_DATA = {
    "put_uco": put_uco, "call_uco": call_uco,
    "put_saf": put_saf, "call_saf": call_saf,
    "net_cost_bbl": net_cost_bbl, "net_cost_annual": net_cost_annual,
    "uco_x": uco_x, "mg_nh_uco": mg_nh_uco,
    "mg_col_uco": mg_col_uco, "mg_put_uco": mg_put_uco,
    "saf_x": saf_x, "mg_nh_saf": mg_nh_saf, "mg_col_saf": mg_col_saf,
}

print("── Black-Scholes Collar Valuation ──────────────────")
print(f"  UCO Leg → Put: ${put_uco:.2f}/bbl  |  Call: ${call_uco:.2f}/bbl")
print(f"  SAF Leg → Put: ${put_saf:.2f}/bbl  |  Call: ${call_saf:.2f}/bbl")
print(f"  Net Collar Cost: ${net_cost_bbl:.2f}/bbl  "
      f"(${net_cost_annual/1e6:.2f}M/year)")
flag = "✔ Approximately Zero-Cost" if abs(net_cost_bbl) < 2.0 else "⚠ Recalibrate strikes"
print(f"  Structure: {flag}")

# %% [markdown]
# ## 12 · Chart 5 — Collar Payoff: UCO Leg

# %%
fig, ax = plt.subplots(figsize=FIG_SIZE)

l1, = ax.plot(uco_x, mg_nh_uco,  color=C["red"],    lw=2.2, ls="--",
              label="Unhedged Margin")
l2, = ax.plot(uco_x, mg_put_uco, color=C["orange"], lw=1.6, ls=":",
              label="Put Only")
l3, = ax.plot(uco_x, mg_col_uco, color=C["green"],  lw=2.5,
              label="Zero-Cost Collar")

p1 = ax.fill_between(uco_x, mg_nh_uco, mg_col_uco,
                     where=(mg_col_uco > mg_nh_uco),
                     alpha=0.2, color=C["green"],
                     label="Active Protection  (UCO > Cap)")
p2 = ax.fill_between(uco_x, mg_nh_uco, mg_col_uco,
                     where=(mg_col_uco < mg_nh_uco),
                     alpha=0.2, color=C["orange"],
                     label="Opportunity Cost  (UCO < Floor)")

ax.axhline(0, color="black", lw=0.9)

# Strike annotations anchored at 78% of Y range
y_lo = min(mg_col_uco.min(), mg_nh_uco.min())
y_hi = max(mg_col_uco.max(), mg_nh_uco.max())
y_a  = y_lo + (y_hi - y_lo) * 0.78

for strike, lbl in [(C_inp["uco_floor"], f"Floor\n${C_inp['uco_floor']}/bbl"),
                    (C_inp["uco_cap"],   f"Cap\n${C_inp['uco_cap']}/bbl")]:
    ax.axvline(strike, color=C["navy"], lw=1.1, ls=":", alpha=0.80)
    ax.text(strike + 1.5, y_a, lbl, fontsize=LABEL_SIZE, color=C["navy"], va="bottom")

ax.legend(handles=[l1, l2, l3, p1, p2], fontsize=LABEL_SIZE, ncol=3,
          loc="upper left", bbox_to_anchor=(0.0, 1.05),
          frameon=True, framealpha=0.9, edgecolor="#cccccc")

_style(ax,
       title="",
       xlabel="UCO Spot Price ($/bbl)",
       ylabel="Operational Margin ($/bbl)")

# Forzamos al título a separarse de la gráfica y centrarse
ax.set_title("Collar Payoff — UCO Leg  (Raw Material Side)", pad=20, 
               fontsize=TITLE_SIZE, fontweight="bold", color=C["blue"], loc="center")

_save(fig, "5_UCO_Collar_Payoff.png")

# %% [markdown]
# ## 13 · Chart 6 — Collar Payoff: SAF Leg

# %%
fig, ax = plt.subplots(figsize=FIG_SIZE)

l1, = ax.plot(saf_x, mg_nh_saf,  color=C["red"],   lw=2.2, ls="--",
              label="Unhedged Margin")
l2, = ax.plot(saf_x, mg_col_saf, color=C["green"], lw=2.5,
              label="Zero-Cost Collar")

p1 = ax.fill_between(saf_x, mg_col_saf, mg_nh_saf,
                     where=(mg_col_saf >= mg_nh_saf),
                     alpha=0.2, color=C["green"],
                     label="Revenue Floor Guaranteed  (SAF < Floor)")
p2 = ax.fill_between(saf_x, mg_col_saf, mg_nh_saf,
                     where=(mg_col_saf < mg_nh_saf),
                     alpha=0.2, color=C["orange"],
                     label="Upside Surrendered  (SAF > Cap)")

ax.axhline(0, color="black", lw=0.9)

y_lo2 = min(mg_col_saf.min(), mg_nh_saf.min())
y_hi2 = max(mg_col_saf.max(), mg_nh_saf.max())
y_a2  = y_lo2 + (y_hi2 - y_lo2) * 0.10

for strike, lbl in [(C_inp["saf_floor"], f"Floor\n${C_inp['saf_floor']}/bbl"),
                    (C_inp["saf_cap"],   f"Cap\n${C_inp['saf_cap']}/bbl")]:
    ax.axvline(strike, color=C["navy"], lw=1.1, ls=":", alpha=0.80)
    ax.text(strike + 2, y_a2, lbl, fontsize=LABEL_SIZE, color=C["navy"], va="top")

ax.legend(handles=[l1, l2, p1, p2], fontsize=LABEL_SIZE, ncol=2,
          loc="upper left", bbox_to_anchor=(0.0, 1.05),
          frameon=True, framealpha=0.9, edgecolor="#cccccc")

_style(ax,
       title="",
       xlabel="SAF Spot Price ($/bbl)",
       ylabel="Operational Margin ($/bbl)")

# Forzamos al título a separarse de la gráfica y centrarse
ax.set_title("Collar Payoff — SAF Leg  (Product Side)", pad=20, 
               fontsize=TITLE_SIZE, fontweight="bold", color=C["blue"], loc="center")

_save(fig, "6_SAF_Collar_Payoff.png")

# %% [markdown]
# ## 14 · Chart 7 — Fan Chart: Cumulative FCF Percentiles

# %%
fan  = RISK_DATA["fan_data"]
yrs  = fan.index.values

avg_ds_m = float(df.loc[1:, "Debt_Service"].mean()) / 1e6
ds_cum   = np.concatenate([[0],
           np.cumsum(np.full(N, avg_ds_m))])

fig, ax = plt.subplots(figsize=FIG_SIZE)

b1 = ax.fill_between(yrs, fan["P10"], fan["P90"],
                     alpha=0.12, color=C["blue"], label="P10–P90 Range")
b2 = ax.fill_between(yrs, fan["P25"], fan["P75"],
                     alpha=0.22, color=C["blue"], label="P25–P75 Range (IQR)")

l50, = ax.plot(yrs, fan["P50"], color=C["blue"],  lw=2.5, zorder=5,
               label="P50 — Median")
l90, = ax.plot(yrs, fan["P90"], color=C["green"], lw=1.5, ls="--", zorder=4,
               label="P90 — Optimistic")
l10, = ax.plot(yrs, fan["P10"], color=C["red"],   lw=1.5, ls="--", zorder=4,
               label="P10 — Pessimistic")
lds, = ax.plot(yrs, -ds_cum, color="black", lw=1.8, ls="-.", zorder=4,
               label="Cumulative Debt Service")

ax.axhline(0, color="black", lw=0.8, ls="--")

# DS Year 1 annotation
ds_yr1_m = float(df.loc[1, "Debt_Service"]) / 1e6
ax.annotate(
    f"DS Yr 1:\n${ds_yr1_m:,.0f}M",
    xy=(1, -ds_cum[1]), xytext=(0.02, 0.3),
    textcoords="axes fraction", fontsize=LABEL_SIZE, color="black",
    arrowprops=dict(arrowstyle="->", color="#555555", lw=0.9),
    bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
              alpha=1, edgecolor="#cccccc")
)

# Bankability badge
p10_end = fan.loc[N, "P10"]
ds_end  = -ds_cum[-1]
badge   = ("✔  Bankable  (P10 > Debt Service)"
           if p10_end > ds_end
           else "⚠  P10 < Debt Service — Review Structure")
badge_c = C["green"] if p10_end > ds_end else C["red"]
#badge_b = "#d5f5e3"  if p10_end > ds_end else "#fadbd8"

ax.text(0.025, 0.6725, badge, transform=ax.transAxes,
        ha="left", va="top", fontsize=LABEL_SIZE,
        color=badge_c, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                  alpha=0.8, edgecolor=badge_c))

ax.yaxis.set_major_formatter(tkr.StrMethodFormatter("{x:,.0f}"))

ax.legend(handles=[b1, b2, l50, l90, l10, lds],
          fontsize=LABEL_SIZE, ncol=1,
          loc="upper left", bbox_to_anchor=(0.01, 1.0),
          frameon=True, framealpha=1, edgecolor="#cccccc")

_style(ax,
       title="",
       xlabel="Project Year",
       ylabel="Cumulative FCF (M USD)")

# Forzamos al título a separarse de la gráfica y centrarse
ax.set_title("Fan Chart — Cumulative FCF: P10 / P50 / P90  (Monte Carlo)", pad=10, 
               fontsize=TITLE_SIZE, fontweight="bold", color=C["blue"], loc="center")

plt.subplots_adjust(right=0.78)   # room for right-side legend
_save(fig, "7_Fan_Chart.png")

# %% [markdown]
# ## 15 · Chart 8 — DSCR Timeline

# %%
dscr_s   = df.loc[1:, "DSCR"]
dscr_v   = dscr_s.values

bar_c = [C["green"]  if v >= 1.50 else
         C["orange"] if v >= 1.20 else C["red"]
         for v in dscr_v]

fig, ax = plt.subplots(figsize=FIG_SIZE)
ax.bar(dscr_s.index, dscr_v, color=bar_c, alpha=0.85, width=0.6, zorder=2)

ax.axhline(1.20, color=C["red"],   lw=1.9, ls="--", zorder=3)
ax.axhline(1.50, color=C["green"], lw=1.6, ls=":",  zorder=3)
ax.axhline(1.00, color="black",    lw=1.0,           zorder=3)

# Dynamic Y cap — prevent Year-1 outlier from flattening the chart
dscr_p90 = float(np.percentile(dscr_v, 90))
dscr_yr1 = float(dscr_v[0])
ylim_top = max(dscr_p90 * 1.35, 2.80)
ax.set_ylim(0, ylim_top)

if dscr_yr1 > ylim_top:
    ax.text(0.07, 0.93,
            f"Year 1 DSCR: {dscr_yr1:.2f}x  ↑  (axis truncated for readability)",
            transform=ax.transAxes, ha="left", va="top", fontsize=LABEL_SIZE,
            color=C["blue"],
            bbox=dict(boxstyle="round,pad=0.28", facecolor="#dce8f5",
                      alpha=0.92, edgecolor="none"))

yr_min   = int(dscr_s.idxmin())
dscr_min = float(dscr_s.min())
if dscr_min <= ylim_top * 0.92:
    ax.annotate(
        f"Min DSCR: {dscr_min:.2f}x\n(Year {yr_min})",
        xy=(yr_min, dscr_min),
        xytext=(yr_min + 1.6, dscr_min + ylim_top * 0.16),
        fontsize=LABEL_SIZE,
        arrowprops=dict(arrowstyle="->", color="#333333", lw=1.1)
    )

ax.set_xticks(dscr_s.index)

patches = [
    mpatches.Patch(color=C["green"],
                   label="DSCR ≥ 1.50x  —  Healthy Zone"),
    mpatches.Patch(color=C["orange"],
                   label="1.20x ≤ DSCR < 1.50x  —  Under Surveillance"),
    mpatches.Patch(color=C["red"],
                   label="DSCR < 1.20x  —  Covenant Breach"),
]
ax.legend(handles=patches, fontsize=LABEL_SIZE, ncol=1,
          loc="upper left", bbox_to_anchor=(0.0, 1),
          frameon=True, framealpha=0.9, edgecolor="#cccccc")

_style(ax,
       title="",
       xlabel="Project Year",
       ylabel="DSCR (×)")

# Forzamos al título a separarse de la gráfica y centrarse
ax.set_title("DSCR Timeline — Annual Debt Service Coverage", pad=10, 
               fontsize=TITLE_SIZE, fontweight="bold", color=C["blue"], loc="center")

_save(fig, "8_DSCR_Timeline.png")

# %% [markdown]
# ---
# ## 16 · Executive Summary Table
#
# All key financial metrics in one place.
# Re-run this cell any time to refresh the table after changing inputs.

# %%
irr_disp   = f"{irr_val*100:.2f}%"   if irr_val   else "N/A"
rm_disp    = f"{MACRO['market_return']*100:.2f}%" if MACRO["market_return"] else "N/A"
ke_disp    = f"{WACC_DATA['ke']*100:.2f}%"        if WACC_DATA["ke"]        else "Manual"
dscr_flag  = "✔ OK" if df.loc[1:,"DSCR"].min() >= 1.20 else "✘ COVENANT BREACH"
zc_flag    = "✔ ~Zero-Cost" if abs(net_cost_bbl) < 2.0 else "⚠ Recalibrate"

summary = {
    # ── Section A: Inputs ────────────────────────────────────────────────────
    "A1 · CAPEX":                f"${A['capex_usd']/1e6:.0f}M",
    "A2 · SAF Price":            f"${A['saf_price_per_bbl']}/bbl",
    "A3 · UCO Cost":             f"${A['uco_cost_per_bbl']}/bbl",
    "A4 · OPEX":                 f"${A['opex_per_bbl']}/bbl",
    "A5 · Capacity":             f"{A['capacity_bpd']:,} bpd",
    "A6 · Annual Volume":        f"{ann_vol:,.0f} bbl/yr",
    "A7 · Project Life":         f"{N} years",
    "A8 · Depreciation":         A["depr_method"],
    "A9 · NWC":                  f"{A['nwc_pct']*100:.0f}% of Revenue",
    # ── Section B: WACC ──────────────────────────────────────────────────────
    "B1 · Beta (Proxy: {})".format(A["ticker"]): f"{MACRO['beta']:.2f}x",
    "B2 · Risk-Free Rate (Rf)":  f"{MACRO['risk_free_rate']*100:.2f}%",
    "B3 · Market Return (Rm)":   rm_disp,
    "B4 · Cost of Equity (Ke)":  ke_disp,
    "B5 · Kd After-Tax":         f"{WACC_DATA['kd_after_tax']*100:.2f}%",
    "B6 · WACC  ◄":              f"{wacc*100:.2f}%",
    # ── Section C: Capital Budgeting ─────────────────────────────────────────
    "C1 · NPV":                  f"${npv_val/1e6:,.1f}M",
    "C2 · IRR":                  irr_disp,
    "C3 · Payback Period":       f"{payback:.2f} years",
    "C4 · Break-Even SAF Price": f"${breakeven_saf:.1f}/bbl",
    "C5 · Min DSCR":             f"{df.loc[1:,'DSCR'].min():.2f}x  ({dscr_flag})",
    # ── Section D: Monte Carlo ───────────────────────────────────────────────
    "D1 · Mean NPV (MC)":        f"${RISK_DATA['mean_npv']/1e6:,.1f}M",
    "D2 · P(NPV > 0)":           f"{RISK_DATA['prob_success']:.1f}%",
    "D3 · VaR (5th percentile)": f"${RISK_DATA['var_5']/1e6:,.1f}M",
    "D4 · VaR (10th percentile)":f"${RISK_DATA['var_10']/1e6:,.1f}M",
    "D5 · Simulations":          f"{B['n_sims']:,} scenarios",
    # ── Section E: Collar ────────────────────────────────────────────────────
    "E1 · UCO Floor / Cap":      f"${C_inp['uco_floor']} / ${C_inp['uco_cap']} per bbl",
    "E2 · SAF Floor / Cap":      f"${C_inp['saf_floor']} / ${C_inp['saf_cap']} per bbl",
    "E3 · Net Collar Cost":      f"${net_cost_bbl:.2f}/bbl  ({zc_flag})",
    "E4 · Annual Collar Cost":   f"${net_cost_annual/1e6:.2f}M/year",
    "E5 · Min Crack Spread":     f"${C_inp['saf_floor'] - C_inp['uco_cap'] - A['opex_per_bbl']:.0f}/bbl (hedged floor)",
}

summary_df = pd.DataFrame(summary.items(), columns=["Metric", "Value"])
summary_df = summary_df.set_index("Metric")

# Colour-code section headers
def _colour_rows(row):
    section = row.name[0]
    colours = {"A": "#eaf4fb", "B": "#eafaf1",
                "C": "#fef9e7", "D": "#fdf2f8", "E": "#fdfefe"}
    bg = colours.get(section, "white")
    return [f"background-color: {bg}"] * len(row)

display(summary_df.style
        .apply(_colour_rows, axis=1)
        .set_properties(**{"font-size": "11px", "text-align": "left"})
        .set_table_styles([
            {"selector": "th",
             "props": [("font-size", "11px"), ("font-weight", "bold"),
                       ("background-color", "#16213e"), ("color", "white")]},
            {"selector": "caption",
             "props": [("caption-side", "top"), ("font-size", "13px"),
                       ("font-weight", "bold"), ("color", "#16213e")]}
        ])
        .set_caption("SAF Bio-Refinery | Executive Financial Summary")
       )

print("\n✅ All charts and summary complete.")
print("   PNG files saved in your working directory.")
