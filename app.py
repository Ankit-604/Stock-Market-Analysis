"""
NSE Golden-Cross Dashboard  |  Streamlit
Six NSE stocks, Jan 2015 - Jul 2018. All signals are computed with SQL window
functions (run on an in-memory SQLite database, the same logic as the MySQL script).

Run:  pip install -r requirements.txt
      streamlit run app.py
Put the six CSV files in a ./data folder next to this file, or upload them in the sidebar.
"""
import glob
import io
import os
import sqlite3
from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="NSE Golden Cross Dashboard", page_icon="📈", layout="wide")

COLS = ["date", "open_price", "high_price", "low_price", "close_price", "wap", "no_of_shares",
        "no_of_trades", "total_turnover", "deliverable_qty", "pct_deli_qty",
        "spread_high_low", "spread_close_open"]
FILE_HINTS = {"bajaj": "Bajaj Auto", "eicher": "Eicher Motors", "hero": "Hero Motocorp",
              "infosys": "Infosys", "tcs": "TCS", "tvs": "TVS Motors"}
GREEN, RED, BLUE, ORANGE, GREY = "#1e8449", "#c0392b", "#1f77b4", "#e67e22", "#9aa5b1"

# --------------------------------------------------------------------------------------
# SQL (same logic as the MySQL script: Tasks 5, 7 and 10)
# --------------------------------------------------------------------------------------
SIGNALS_SQL = """
WITH adj AS (
  SELECT p.stock, p.date, p.close_price AS raw_close,
         CASE WHEN :adjust = 1 THEN p.close_price / COALESCE(e.factor, 1.0)
              ELSE p.close_price END AS close_price
  FROM prices p
  LEFT JOIN events e ON e.stock = p.stock AND p.date < e.event_date      -- prices BEFORE the event
),
ma AS (
  SELECT stock, date, raw_close, close_price,
    CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 20
         THEN AVG(close_price) OVER (PARTITION BY stock ORDER BY date
              ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) END AS ma20,
    CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 50
         THEN AVG(close_price) OVER (PARTITION BY stock ORDER BY date
              ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) END AS ma50
  FROM adj
),
lagged AS (
  SELECT *, LAG(ma20) OVER (PARTITION BY stock ORDER BY date) AS prev_ma20,
            LAG(ma50) OVER (PARTITION BY stock ORDER BY date) AS prev_ma50
  FROM ma
)
SELECT stock, date, raw_close, close_price, ma20, ma50,
  CASE
    WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
    WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
    WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell'
    ELSE 'Hold'
  END AS signal
FROM lagged
ORDER BY stock, date
"""

WORST_DAY_SQL = """
WITH moves AS (
  SELECT stock, date, close_price,
         100.0 * (close_price / LAG(close_price) OVER (PARTITION BY stock ORDER BY date) - 1) AS pct_move
  FROM prices
),
ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY stock ORDER BY pct_move) AS rn
  FROM moves WHERE pct_move IS NOT NULL
)
SELECT stock, date, close_price, ROUND(pct_move, 1) AS pct_move
FROM ranked WHERE rn = 1 ORDER BY pct_move
"""


# --------------------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------------------
def stock_from_filename(name: str):
    low = os.path.basename(name).lower()
    for hint, stock in FILE_HINTS.items():
        if hint in low:
            return stock
    return None


@st.cache_data(show_spinner=False)
def load_prices(files: tuple) -> pd.DataFrame:
    """files = ((filename, bytes), ...) -> long dataframe, one row per stock per day."""
    frames = []
    for name, raw in files:
        stock = stock_from_filename(name)
        if stock is None:
            continue
        df = pd.read_csv(io.BytesIO(raw))
        df = df.iloc[:, :13]
        df.columns = COLS
        df["date"] = pd.to_datetime(df["date"].astype(str).str.strip(), format="%d-%B-%Y")
        df.insert(0, "stock", stock)
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True).sort_values(["stock", "date"]).reset_index(drop=True)
    return out


def read_source_files(uploaded):
    if uploaded:
        return tuple((f.name, f.getvalue()) for f in uploaded)
    here = os.path.dirname(os.path.abspath(__file__))
    paths = sorted(glob.glob(os.path.join(here, "data", "*.csv")) + glob.glob(os.path.join(here, "*.csv")))
    return tuple((p, open(p, "rb").read()) for p in paths)


def sqlite_con(prices: pd.DataFrame, events: pd.DataFrame) -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    p = prices[["stock", "date", "close_price"]].copy()
    p["date"] = p["date"].dt.strftime("%Y-%m-%d")
    p.to_sql("prices", con, index=False)
    e = events.copy()
    if e.empty:
        e = pd.DataFrame({"stock": [], "event_date": [], "factor": []})
    e.to_sql("events", con, index=False)
    return con


@st.cache_data(show_spinner=False)
def compute_signals(prices: pd.DataFrame, events: pd.DataFrame, adjust: bool) -> pd.DataFrame:
    con = sqlite_con(prices, events)
    df = pd.read_sql_query(SIGNALS_SQL, con, params={"adjust": int(adjust)})
    con.close()
    df["date"] = pd.to_datetime(df["date"])
    return df


@st.cache_data(show_spinner=False)
def compute_worst_days(prices: pd.DataFrame) -> pd.DataFrame:
    con = sqlite_con(prices, pd.DataFrame())
    df = pd.read_sql_query(WORST_DAY_SQL, con)
    con.close()
    return df


# --------------------------------------------------------------------------------------
# Analysis helpers
# --------------------------------------------------------------------------------------
def summarise(sig: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for stock, d in sig.groupby("stock"):
        d = d.reset_index(drop=True)
        ev = d[d["signal"] != "Hold"]
        last = ev.iloc[-1] if len(ev) else None
        first_c, last_c = d["close_price"].iloc[0], d["close_price"].iloc[-1]
        m20, m50 = d["ma20"].iloc[-1], d["ma50"].iloc[-1]
        gaps = ev["date"].diff().dt.days
        rows.append({
            "Stock": stock,
            "First close": first_c, "Last close": last_c,
            "Change %": 100 * (last_c / first_c - 1),
            "Buys": int((d["signal"] == "Buy").sum()), "Sells": int((d["signal"] == "Sell").sum()),
            "Last signal": last["signal"] if last is not None else "-",
            "Last signal date": last["date"].date() if last is not None else None,
            "20d on last day": m20, "50d on last day": m50,
            "Trend now": "20d above 50d" if m20 > m50 else "20d below 50d",
            "Signals within 30 days of the previous": int((gaps < 30).sum()),
        })
    return pd.DataFrame(rows)


def backtest(sig: pd.DataFrame, cost_pct: float):
    """Long-only: buy at each Buy close, sell at the next Sell close; cash earns nothing.
    An open trade is valued at the last close. cost_pct is charged on each side."""
    trades, summary = [], []
    c = cost_pct / 100.0
    for stock, d in sig.groupby("stock"):
        d = d.reset_index(drop=True)
        pos, stock_trades = None, []
        for i, r in d.iterrows():
            if r["signal"] == "Buy" and pos is None:
                pos = i
            elif r["signal"] == "Sell" and pos is not None:
                stock_trades.append((pos, i, False))
                pos = None
        if pos is not None:
            stock_trades.append((pos, len(d) - 1, True))
        growth = 1.0
        for a, b, is_open in stock_trades:
            gross = d.loc[b, "close_price"] / d.loc[a, "close_price"] - 1
            net = (1 + gross) * (1 - c) ** 2 - 1
            growth *= 1 + net
            trades.append({"Stock": stock, "Buy date": d.loc[a, "date"].date(),
                           "Exit date": d.loc[b, "date"].date(),
                           "Exit type": "Open (last close)" if is_open else "Sell signal",
                           "Buy price": d.loc[a, "close_price"], "Exit price": d.loc[b, "close_price"],
                           "Trade return %": 100 * net})
        hold = 100 * (d["close_price"].iloc[-1] / d["close_price"].iloc[0] - 1)
        wins = sum(1 for t in trades if t["Stock"] == stock and t["Trade return %"] > 0)
        summary.append({"Stock": stock, "Trades": len(stock_trades), "Winning trades": wins,
                        "Signal strategy %": 100 * (growth - 1), "Buy & hold %": hold})
    return pd.DataFrame(summary), pd.DataFrame(trades)


def fmt_pct(x):
    return f"{x:+.1f}%"


# --------------------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------------------
st.sidebar.title("📈 Controls")
uploaded = st.sidebar.file_uploader("Upload the six CSV files (optional)", type="csv", accept_multiple_files=True,
                                    help="If you skip this, the app reads the CSVs from the ./data folder.")
files = read_source_files(uploaded)
prices = load_prices(files) if files else pd.DataFrame()

if prices.empty:
    st.title("NSE Golden Cross Dashboard")
    st.info("No data found. Put Bajaj_Auto.csv, Eicher_Motors.csv, Hero_Motocorp.csv, Infosys.csv, TCS.csv and "
            "TVS_Motors.csv in a `data` folder next to app.py, or upload them in the sidebar.")
    st.stop()

stocks = sorted(prices["stock"].unique())

st.sidebar.markdown("---")
adjust = st.sidebar.toggle("Adjust for bonus issues", value=True,
                           help="Divides prices before each event date by the factor, so the 50% price cliff disappears.")
st.sidebar.caption("Events found in the data (change them if your records say otherwise):")
events_rows = []
defaults = {"TCS": (date(2018, 5, 31), 2.0), "Infosys": (date(2015, 6, 15), 2.0)}
for s, (d0, f0) in defaults.items():
    if s in stocks:
        c1, c2 = st.sidebar.columns([3, 2])
        ev_date = c1.date_input(f"{s} event date", d0, key=f"d_{s}")
        factor = c2.number_input("Factor", min_value=1.0, value=f0, step=0.5, key=f"f_{s}")
        events_rows.append({"stock": s, "event_date": ev_date.strftime("%Y-%m-%d"), "factor": float(factor)})
events = pd.DataFrame(events_rows)

st.sidebar.markdown("---")
cost = st.sidebar.slider("Cost per trade side (%)", 0.0, 0.5, 0.0, 0.05,
                         help="Brokerage and slippage charged on both buy and sell in the strategy test.")

sig = compute_signals(prices, events, adjust)
sig_raw = compute_signals(prices, events, False)
sig_adj = compute_signals(prices, events, True)
summary = summarise(sig)
summary_raw, summary_adj = summarise(sig_raw), summarise(sig_adj)

# --------------------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------------------
st.title("NSE Golden Cross Dashboard")
st.caption(f"{len(stocks)} stocks · {prices['date'].min().date()} to {prices['date'].max().date()} · "
           f"{prices.groupby('stock').size().iloc[0]} trading days each · "
           f"prices shown are {'ADJUSTED for bonus issues' if adjust else 'RAW (unadjusted)'}")

tab_over, tab_price, tab_trap, tab_strat, tab_ins = st.tabs(
    ["Overview", "Price & signals", "Data trap", "Strategy test", "Insights & recommendations"])

# --------------------------------------------------------------------------------------
# Overview
# --------------------------------------------------------------------------------------
with tab_over:
    best, worst = summary.loc[summary["Change %"].idxmax()], summary.loc[summary["Change %"].idxmin()]
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Best performer", best["Stock"], fmt_pct(best["Change %"]))
    k2.metric("Weakest performer", worst["Stock"], fmt_pct(worst["Change %"]))
    k3.metric("Total Buy signals", int(summary["Buys"].sum()))
    k4.metric("Total Sell signals", int(summary["Sells"].sum()))

    st.subheader("Summary by stock")
    show = summary.copy()
    for col in ["First close", "Last close", "20d on last day", "50d on last day"]:
        show[col] = show[col].round(2)
    show["Change %"] = show["Change %"].round(1)
    st.dataframe(show, width="stretch", hide_index=True)

    st.subheader("Raw vs adjusted price change")
    cmp_df = pd.DataFrame({"Stock": summary_raw["Stock"], "Raw": summary_raw["Change %"].values,
                           "Adjusted": summary_adj["Change %"].values}).melt("Stock", var_name="Prices", value_name="Change %")
    fig = px.bar(cmp_df, x="Stock", y="Change %", color="Prices", barmode="group",
                 color_discrete_map={"Raw": RED, "Adjusted": GREEN})
    fig.update_layout(height=380, margin=dict(t=20, b=10))
    st.plotly_chart(fig, width="stretch")
    st.caption("TCS and Infosys look like losers on raw prices only because of the 1:1 bonus issues.")

    st.subheader("Compare stocks (rebased to 100)")
    chosen = st.multiselect("Stocks", stocks, default=stocks)
    fig = go.Figure()
    for s in chosen:
        d = sig[sig["stock"] == s]
        fig.add_trace(go.Scatter(x=d["date"], y=100 * d["close_price"] / d["close_price"].iloc[0], name=s, mode="lines"))
    fig.update_layout(height=420, yaxis_title="Rebased close (start = 100)", margin=dict(t=20, b=10),
                      legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig, width="stretch")

# --------------------------------------------------------------------------------------
# Price & signals
# --------------------------------------------------------------------------------------
with tab_price:
    c1, c2 = st.columns([1, 2])
    stock = c1.selectbox("Stock", stocks, index=stocks.index("Bajaj Auto") if "Bajaj Auto" in stocks else 0)
    dmin, dmax = sig["date"].min().date(), sig["date"].max().date()
    rng = c2.slider("Date range", dmin, dmax, (dmin, dmax))
    d = sig[sig["stock"] == stock]
    dv = d[(d["date"].dt.date >= rng[0]) & (d["date"].dt.date <= rng[1])]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dv["date"], y=dv["close_price"], name="Close", line=dict(color=GREY, width=1.3)))
    fig.add_trace(go.Scatter(x=dv["date"], y=dv["ma20"], name="20-day average", line=dict(color=BLUE, width=1.6)))
    fig.add_trace(go.Scatter(x=dv["date"], y=dv["ma50"], name="50-day average", line=dict(color=ORANGE, width=1.6)))
    b, s_ = dv[dv["signal"] == "Buy"], dv[dv["signal"] == "Sell"]
    fig.add_trace(go.Scatter(x=b["date"], y=b["close_price"], mode="markers", name="Buy",
                             marker=dict(symbol="triangle-up", size=13, color=GREEN, line=dict(width=1, color="white"))))
    fig.add_trace(go.Scatter(x=s_["date"], y=s_["close_price"], mode="markers", name="Sell",
                             marker=dict(symbol="triangle-down", size=13, color=RED, line=dict(width=1, color="white"))))
    fig.update_layout(height=520, yaxis_title="Price (Rs.)", margin=dict(t=20, b=10), hovermode="x unified",
                      legend=dict(orientation="h", y=1.07))
    st.plotly_chart(fig, width="stretch")

    row = summary[summary["Stock"] == stock].iloc[0]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Buys / Sells", f"{row['Buys']} / {row['Sells']}")
    m2.metric("Latest signal", f"{row['Last signal']}", str(row["Last signal date"]), delta_color="off")
    m3.metric("Change over the period", fmt_pct(row["Change %"]))
    m4.metric("Signals within 30 days of previous", int(row["Signals within 30 days of the previous"]))

    st.subheader("Signal list")
    ev = d[d["signal"] != "Hold"][["date", "signal", "close_price", "ma20", "ma50"]].copy()
    ev["days since previous signal"] = ev["date"].diff().dt.days
    ev["date"] = ev["date"].dt.date
    st.dataframe(ev.round(2), width="stretch", hide_index=True)

    with st.expander("Day lookup (Task 9)"):
        pick = st.date_input("Pick a date", value=date(2018, 6, 21), min_value=dmin, max_value=dmax, key="lookup")
        hit = d[d["date"].dt.date == pick]
        st.write(f"Signal on {pick}: **{hit['signal'].iloc[0]}**" if len(hit)
                 else f"No row for {pick}: the market was closed that day.")

    with st.expander("Show the SQL used for the averages and signals"):
        st.code(SIGNALS_SQL, language="sql")

# --------------------------------------------------------------------------------------
# Data trap
# --------------------------------------------------------------------------------------
with tab_trap:
    st.subheader("Each stock's single worst day (raw prices)")
    worst_df = compute_worst_days(prices)
    colors = [RED if v < -20 else BLUE for v in worst_df["pct_move"]]
    fig = go.Figure(go.Bar(x=worst_df["stock"], y=worst_df["pct_move"], marker_color=colors,
                           text=worst_df["pct_move"].astype(str) + "%", textposition="outside"))
    fig.update_layout(height=360, yaxis_title="Worst one-day move (%)", margin=dict(t=20, b=10))
    st.plotly_chart(fig, width="stretch")
    st.dataframe(worst_df, width="stretch", hide_index=True)
    st.warning("Two moves of about −50% in one day (Infosys, TCS) are not crashes. They are 1:1 bonus issues: "
               "the share count doubled and the price halved, with no loss of value.")

    cA, cB = st.columns([1, 3])
    s_trap = cA.selectbox("Stock to inspect", [s for s in ["TCS", "Infosys"] if s in stocks] +
                          [s for s in stocks if s not in ("TCS", "Infosys")], key="trap")
    d = sig_raw[sig_raw["stock"] == s_trap][["date", "close_price"]].rename(columns={"close_price": "Raw close"})
    d["Adjusted close"] = sig_adj[sig_adj["stock"] == s_trap]["close_price"].values
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d["date"], y=d["Raw close"], name="Raw close", line=dict(color=RED, width=1.4)))
    fig.add_trace(go.Scatter(x=d["date"], y=d["Adjusted close"], name="Adjusted close", line=dict(color=GREEN, width=1.4)))
    fig.update_layout(height=400, margin=dict(t=20, b=10), yaxis_title="Price (Rs.)", legend=dict(orientation="h", y=1.08))
    cB.plotly_chart(fig, width="stretch")

    st.subheader("What changed after the fix")
    chg = summary_raw[["Stock", "Change %", "Buys", "Sells", "Last signal", "Last signal date"]].merge(
        summary_adj[["Stock", "Change %", "Buys", "Sells", "Last signal", "Last signal date"]],
        on="Stock", suffixes=(" (raw)", " (adjusted)"))
    chg = chg[(chg["Change % (raw)"].round(1) != chg["Change % (adjusted)"].round(1)) |
              (chg["Buys (raw)"] != chg["Buys (adjusted)"]) | (chg["Sells (raw)"] != chg["Sells (adjusted)"]) |
              (chg["Last signal (raw)"] != chg["Last signal (adjusted)"])]
    st.dataframe(chg.round(1), width="stretch", hide_index=True)
    st.caption("Only stocks whose result changed are listed. The bonus dates were inferred from the price pattern; "
               "confirm them against exchange corporate-action records.")

# --------------------------------------------------------------------------------------
# Strategy test
# --------------------------------------------------------------------------------------
with tab_strat:
    st.subheader("If you had followed the signals")
    st.write("Buy at the close on each Buy signal, sell at the close on the next Sell signal, hold cash in between "
             "(earning nothing). A trade still open on the last day is valued at the last close. "
             f"Cost per side: **{cost:.2f}%** (change it in the sidebar).")
    bt_sum, bt_trades = backtest(sig, cost)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=bt_sum["Stock"], y=bt_sum["Signal strategy %"], name="Follow the signals", marker_color=BLUE))
    fig.add_trace(go.Bar(x=bt_sum["Stock"], y=bt_sum["Buy & hold %"], name="Buy & hold", marker_color=GREY))
    fig.update_layout(barmode="group", height=380, yaxis_title="Return (%)", margin=dict(t=20, b=10),
                      legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig, width="stretch")
    st.dataframe(bt_sum.round(1), width="stretch", hide_index=True)
    lag = int((bt_sum["Signal strategy %"] < bt_sum["Buy & hold %"]).sum())
    st.info(f"The signal strategy trailed buy-and-hold on {lag} of {len(bt_sum)} stocks.")
    pick = st.selectbox("See the trades for", stocks, key="bt_stock")
    st.dataframe(bt_trades[bt_trades["Stock"] == pick].round(2), width="stretch", hide_index=True)
    st.caption("Single path, in-sample, 3.5 years: this describes what happened, not what will happen. "
               "Taxes and dividends are ignored.")

# --------------------------------------------------------------------------------------
# Insights
# --------------------------------------------------------------------------------------
with tab_ins:
    st.subheader("Key insights")
    st.markdown("""
- **The data trap changes the answer.** Infosys (15 Jun 2015) and TCS (31 May 2018) had 1:1 bonus issues. On raw
  prices they look like losers (−30.9% and −23.8%); adjusted, they gained **+38.2%** and **+52.4%**.
- **The TCS Sell of 5 Jun 2018 was created by the price cliff.** After adjustment, TCS's latest signal is a Buy (20 Apr 2018).
- **Golden crosses lag and whipsaw in sideways markets.** Bajaj Auto had 23 signals, 11 within 30 days of the previous one.
- **Following the signals trailed buy-and-hold on all six stocks** (no costs). Eicher was the cleanest: all 6 trades won.
- **A Sell after a big run is a caution, not proof of a reversal** (Eicher +82.6%, TVS +86.9%).
""")
    st.subheader("Recommendations")
    st.markdown("""
| Item | Recommendation |
|---|---|
| TCS, Infosys | Treat as positive performers; drop the deck's "sell TCS" call. |
| Eicher, TVS | Strong long-run performers; watch the Sell signals as a caution. |
| Bajaj Auto | No clear edge from the signals; wait for confirmation. |
| Hero Motocorp | Weakest case: low return and a Sell signal. |
| Method | Adjust for corporate actions first; add a confirmation filter before trusting a golden cross. |
""")
    st.caption("From this data only: not investment advice. No dividends, costs, valuation, news or market index.")
