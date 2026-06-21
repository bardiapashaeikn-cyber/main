import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


st.title("📊 Market Pattern Look-Alike Engine")

# =========================
# UI
# =========================

st.markdown("""
<style>
.block-container {
    max-width: 900px;
    margin: auto;
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    target = st.text_input("Target Ticker", "SMCI").upper()

with col2:
    lookback = st.slider("Pattern Length (days)", 10, 80, 20)

with col3:
    horizon = st.slider("Forecast Horizon (days)", 1, 30, 5)

col4, col5 = st.columns(2)

with col4:
    years = st.slider("History (years)", 2, 15, 10)

with col5:
    top_n = st.slider("Top Matches", 10, 200, 50)

run = st.button("Run Scan")

# =========================
# STRICT S&P 500 LOADER (NO FALLBACK)
# =========================

@st.cache_data
@st.cache_data
def get_sp500():
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"

    df = pd.read_csv(url)

    if "Symbol" not in df.columns:
        raise ValueError("S&P 500 source failed (missing Symbol column)")

    sp = df["Symbol"].astype(str).tolist()

    # fix tickers (BRK.B → BRK-B)
    sp = [s.replace(".", "-").strip() for s in sp]

    # clean invalid entries
    sp = [s for s in sp if s and len(s) > 0]

    if len(sp) != 503:  # S&P usually 503 due to share classes
        raise ValueError(f"Expected ~500 tickers, got {len(sp)}")

    return sp


# =========================
# DATA LOADING
# =========================

@st.cache_data
def load_data(tickers, years):
    data = {}

    for t in tickers:
        try:
            df = yf.download(t, period=f"{years}y", auto_adjust=True, progress=False)

            if df.empty:
                continue

            close = df["Close"]

            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]

            close = pd.to_numeric(close, errors="coerce").dropna()

            if len(close) > 200:
                data[t] = close

        except:
            continue

    return data


def norm(x):
    x = np.array(x, dtype=float)
    return x / x[0]


def corr(a, b):
    return np.corrcoef(a, b)[0, 1]


# =========================
# RUN
# =========================

if run:

    try:
        universe = get_sp500()
    except Exception as e:
        st.error(f"S&P 500 load failed: {e}")
        st.stop()

    universe = list(set(universe + [target]))

    with st.spinner("Loading market data (S&P 500 only)..."):
        data = load_data(universe, years)

    if target not in data:
        st.error("Target not found in downloaded data")
        st.stop()

    target_series = data[target]
    current = norm(target_series.iloc[-lookback:])

    matches = []

    # =========================
    # SCAN
    # =========================

    for sym, series in data.items():

        arr = series.values
        max_i = len(arr) - lookback - horizon

        if max_i <= 0:
            continue

        for i in range(max_i):

            hist = arr[i:i+lookback]
            fut = arr[i+lookback:i+lookback+horizon]

            if len(hist) < lookback or len(fut) < horizon:
                continue

            h = norm(hist)

            score = corr(current, h)
            if np.isnan(score):
                continue

            matches.append({
                "ticker": sym,
                "date": series.index[i + lookback],
                "score": score,
                "future": float(fut[-1] / hist[-1] - 1),
                "pattern": h,
                "future_path": (fut / hist[-1] - 1)
            })

    df = pd.DataFrame(matches)

    if df.empty:
        st.error("No matches found")
        st.stop()

    df = df.sort_values("score", ascending=False).head(top_n)

    # =========================
    # STATS
    # =========================

    returns = np.array(df["future"]) * 100

    st.subheader("📊 Statistics")

    c1, c2, c3 = st.columns(3)

    c1.metric("Win Rate", f"{(returns > 0).mean():.1%}")
    c2.metric("Avg Return", f"{returns.mean():.2f}%")
    c3.metric("Median", f"{np.median(returns):.2f}%")

    # =========================
    # GRAPH 1
    # =========================

    st.subheader("📌 Current vs Best Match")

    best = df.iloc[0]

    fig, ax = plt.subplots(figsize=(5, 2.8))
    ax.plot(current, label="Current")
    ax.plot(best["pattern"], label=f"{best['ticker']} ({best['date'].date()})")

    ax.set_xlabel("Days")
    ax.set_ylabel("Normalized Price")
    ax.legend()

    st.pyplot(fig)

    # =========================
    # GRAPH 2
    # =========================

    st.subheader("🔍 Top Matches")

    fig, ax = plt.subplots(figsize=(5, 2.8))
    ax.plot(current, linewidth=2)

    for _, r in df.head(10).iterrows():
        ax.plot(r["pattern"], alpha=0.4)

    ax.set_xlabel("Days")
    ax.set_ylabel("Normalized Price")

    st.pyplot(fig)

    # =========================
    # GRAPH 3
    # =========================

    st.subheader("📈 Future Path")

    paths = np.array(df["future_path"].tolist())
    avg = np.mean(paths, axis=0) * 100

    fig, ax = plt.subplots(figsize=(5, 2.8))
    ax.plot(range(1, horizon + 1), avg)
    ax.axhline(0, linestyle="--")

    ax.set_xlabel("Future Days")
    ax.set_ylabel("Return %")

    st.pyplot(fig)

    # =========================
    # GRAPH 4
    # =========================

    st.subheader("📊 Distribution")

    fig, ax = plt.subplots(figsize=(5, 2.8))
    ax.hist(returns, bins=25)
    ax.axvline(returns.mean(), linestyle="--")

    ax.set_xlabel("Return %")
    ax.set_ylabel("Frequency")

    st.pyplot(fig)

    # =========================
    # TABLE
    # =========================

    st.subheader("🏆 Best Matches")

    out = df.copy()
    out["label"] = out["ticker"] + " (" + out["date"].astype(str) + ")"

    table = out[["label", "score", "future"]].copy()
    table["future"] = (table["future"] * 100).round(2)
    table["score"] = table["score"].round(3)

    st.dataframe(table, use_container_width=True)
