import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.title("Intraday Move Analyzer")

ticker_input = st.text_input("Tickers (comma separated)")
threshold_pct = st.number_input("Threshold %", value=1.0)

run = st.button("Run Analysis")

if run and ticker_input:

    tickers = [t.strip().upper() for t in ticker_input.split(",")]

    results = []

    for ticker in tickers:

        data = yf.download(
            ticker,
            start="2000-01-01",
            auto_adjust=True,
            progress=False
        )

        if data.empty:
            continue

        # -----------------------------
        # CLEAN DATA
        # -----------------------------
        close = data["Close"]
        high = data["High"]
        low = data["Low"]

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        if isinstance(high, pd.DataFrame):
            high = high.iloc[:, 0]
        if isinstance(low, pd.DataFrame):
            low = low.iloc[:, 0]

        close = close.squeeze()
        high = high.squeeze()
        low = low.squeeze()

        prev_close = close.shift(1)

        # -----------------------------
        # METRICS
        # -----------------------------
        hit = high >= prev_close
        hit_threshold = high >= prev_close * (1 + threshold_pct / 100)

        intraday_hit_pct = hit.dropna().mean() * 100
        probability_1p = hit_threshold.dropna().mean() * 100

        exceed_pct = ((high / prev_close) - 1) * 100
        exceed_pct = exceed_pct.squeeze()

        all_moves = pd.to_numeric(exceed_pct, errors="coerce").dropna()

        down = ((low / prev_close) - 1) * 100
        down_days = down[down < 0]

        # -----------------------------
        # SAVE RESULTS (your original idea)
        # -----------------------------
        results.append({
            "Ticker": ticker,
            "Hit %": intraday_hit_pct,
            f"+{threshold_pct}% Hit %": probability_1p,
            "Avg Exceed %": exceed_pct[hit].mean(),
            "Avg Down %": down_days.mean(),
            "Worst Down %": down_days.min()
        })

        # -----------------------------
        # PLOT DISTRIBUTION (ONE PER TICKER)
        # -----------------------------
        if ticker == tickers[0]:  # only show first ticker chart (avoid spam)
            fig, ax = plt.subplots(figsize=(10, 5))

            ax.hist(all_moves, bins=50, edgecolor="black")

            if len(all_moves) > 0:
                mean_val = float(all_moves.mean())
                ax.axvline(mean_val, color="red", linestyle="dashed", label="Mean")

            ax.set_title(f"{ticker} Intraday Move Distribution")
            ax.set_xlabel("Intraday Move %")
            ax.set_ylabel("Frequency")
            ax.legend()

            st.pyplot(fig)

    # -----------------------------
    # RESULTS TABLE
    # -----------------------------
    df = pd.DataFrame(results)

    if not df.empty:
        df = df.sort_values(f"+{threshold_pct}% Hit %", ascending=False)
        st.dataframe(df)
