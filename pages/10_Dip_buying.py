import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Intraday Trigger Analyzer",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Intraday Trigger Analyzer")

st.write("""
This tool analyzes what happens AFTER a stock reaches a
specified move from the previous day's close.

Uses FREE Yahoo Finance 2-minute data (~29 days).
""")

# ============================================================
# INPUTS
# ============================================================

col1, col2 = st.columns([1,1])

with col1:

    ticker = st.text_input(
        "Ticker",
        value="AAPL"
    ).upper()

with col2:

    trigger = st.number_input(
        "Trigger (%)",
        value=-5.0,
        step=0.5,
        format="%.2f"
    )

analyze = st.button(
    "🚀 Analyze"
)

# ============================================================
# DOWNLOAD DATA
# ============================================================

@st.cache_data
def load_data(ticker):

    df = yf.download(
        ticker,
        period="60d",
        interval="2m",
        progress=False,
        auto_adjust=False
    )

    if df.empty:
        return pd.DataFrame()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    return df
# ============================================================
# ANALYZE
# ============================================================

if analyze:

    with st.spinner("Downloading 1-minute data..."):

        df = load_data(ticker)

    if df.empty:

        st.error("No data found.")

        st.stop()

    st.success(f"Downloaded {len(df)} one-minute candles.")

    # Time columns

    df["Datetime"] = pd.to_datetime(df["Datetime"])

    df["Day"] = df["Datetime"].dt.date

    # Previous day's close

    daily_close = (
        df.groupby("Day")["Close"]
        .last()
    )

    previous_close = daily_close.shift(1)

    df["Prev Close"] = df["Day"].map(previous_close)

    df = df.dropna().copy()

    st.write(
        f"Trading Days: {df['Day'].nunique()}"
    )

    # ============================================================
    # FIND FIRST TRIGGER OF EACH DAY
    # ============================================================

    results = []

    for day, day_df in df.groupby("Day"):

        day_df = day_df.reset_index(drop=True)

        prev_close = day_df.loc[0, "Prev Close"]

        if pd.isna(prev_close):
            continue

        # Calculate the exact trigger price
        trigger_price = prev_close * (1 + trigger / 100)

        trigger_index = None

        # --------------------------------------------------------
        # Find FIRST trigger minute
        # --------------------------------------------------------

        for i, row in day_df.iterrows():

            if trigger < 0:

                # Price traded down to trigger
                if row["Low"] <= trigger_price:

                    trigger_index = i
                    break

            else:

                # Price traded up to trigger
                if row["High"] >= trigger_price:

                    trigger_index = i
                    break

        if trigger_index is None:
            continue

        # --------------------------------------------------------
        # Skip trigger candle
        # --------------------------------------------------------

        after = day_df.iloc[trigger_index + 1:]

        if after.empty:
            continue

        highest = after["High"].max()
        lowest = after["Low"].min()

        bounce = (
            (highest - trigger_price)
            / trigger_price
            * 100
        )

        drop = (
            (lowest - trigger_price)
            / trigger_price
            * 100
        )

        results.append({

            "Date": day,

            "Trigger Price": trigger_price,

            "Highest After": highest,

            "Lowest After": lowest,

            "Bounce %": bounce,

            "Drop %": drop

        })


    results = pd.DataFrame(results)


    # ============================================================
    # SHOW RESULTS
    # ============================================================

    st.divider()

    st.subheader("Trigger Events")

    if results.empty:

        st.warning("No trigger events found.")

        st.stop()

    display = results.copy()

    display[
        [
            "Trigger Price",
            "Highest After",
            "Lowest After",
            "Bounce %",
            "Drop %"
        ]
    ] = display[
        [
            "Trigger Price",
            "Highest After",
            "Lowest After",
            "Bounce %",
            "Drop %"
        ]
    ].round(2)

    st.write(f"Found **{len(display)}** trigger events.")

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )

    # ============================================================
    # SUMMARY
    # ============================================================

    st.divider()

    st.subheader("Summary")

    total_events = len(results)

    avg_bounce = results["Bounce %"].mean()
    median_bounce = results["Bounce %"].median()

    avg_drop = results["Drop %"].mean()
    median_drop = results["Drop %"].median()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Trigger Events",
        total_events
    )

    c2.metric(
        "Average Bounce",
        f"{avg_bounce:.2f}%"
    )

    c3.metric(
        "Average Drop",
        f"{avg_drop:.2f}%"
    )

    # ============================================================
    # PROBABILITY SETTINGS
    # ============================================================

    st.divider()

    st.subheader("Probability Table")

    step = st.number_input(
        "Step Size (%)",
        min_value=0.25,
        max_value=5.0,
        value=0.50,
        step=0.25
    )

    max_target = st.number_input(
        "Maximum Target (%)",
        min_value=1.0,
        max_value=20.0,
        value=5.0,
        step=0.5
    )

    levels = np.arange(
        step,
        max_target + step,
        step
    )

    # ============================================================
    # CALCULATE PROBABILITIES
    # ============================================================

    table = []

    for level in levels:

        upside = (
            (results["Bounce %"] >= level).mean()
            * 100
        )

        downside = (
            (results["Drop %"] <= -level).mean()
            * 100
        )

        table.append({

            "Target Above Entry (%)": f"+{level:.2f}",

            "Reached Before Close (%)": round(upside, 1),

            "Further Drop Below Entry (%)": f"-{level:.2f}",

            "Reached Before Close (Downside %)": round(downside, 1)

        })

    prob_df = pd.DataFrame(table)

    st.dataframe(
        prob_df,
        use_container_width=True,
        hide_index=True
    )

    # ============================================================
    # HISTOGRAM
    # ============================================================

    st.divider()

    st.subheader("Bounce Distribution")

    fig, ax = plt.subplots(figsize=(9,4))

    ax.hist(
        results["Bounce %"],
        bins=12,
        edgecolor="black"
    )

    ax.set_xlabel("Bounce (%)")
    ax.set_ylabel("Frequency")
    ax.set_title("Distribution of Maximum Bounce")

    st.pyplot(fig)

    # ============================================================
    # DOWNLOAD
    # ============================================================

    csv = results.round(2).to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download Results",
        csv,
        file_name=f"{ticker}_intraday_trigger_results.csv",
        mime="text/csv"
    )
