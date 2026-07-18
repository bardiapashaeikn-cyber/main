import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Failed Recovery Analyzer",
    page_icon="📉",
    layout="wide"
)

st.title("📉 Failed Recovery Analyzer")

st.write(
    """
This tool analyzes historical days where a stock opened at a specified move
from the previous close and **FAILED** to recover back to yesterday's close.

It then calculates how much the stock usually bounced before the end of the day.
"""
)

# ==========================================================
# USER INPUTS
# ==========================================================

col1, col2 = st.columns([0.7, 2.3])

with col1:
    ticker = st.text_input(
        "Ticker",
        value="AAPL"
    ).upper()

with col2:
    years = st.slider(
        "Years of History",
        min_value=1,
        max_value=20,
        value=5
    )


# ==========================================================
# DOWNLOAD DATA
# ==========================================================

@st.cache_data
def load_data(ticker, years):

    end = pd.Timestamp.today()
    start = end - pd.DateOffset(years=years)

    df = yf.download(
        ticker,
        start=start,
        end=end,
        progress=False,
        auto_adjust=False
    )

    if df.empty:
        return df

    # Handle MultiIndex if needed
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    return df

# ==========================================================
# LOAD DATA
# ==========================================================

if st.button("Analyze"):

    with st.spinner("Downloading data..."):

        df = load_data(ticker, years)

    if df.empty:
        st.error("No data found.")
        st.stop()

    st.success(f"Downloaded {len(df)} trading days.")

       # ==========================================================
    # CALCULATIONS
    # ==========================================================

    # Previous day's close
    df["Prev Close"] = df["Close"].shift(1)

    # Remove first row (no previous close)
    df = df.dropna().copy()

    # Opening move from previous close
    df["Open Move %"] = (
        (df["Open"] - df["Prev Close"])
        / df["Prev Close"]
        * 100
    )

    # Daily return (optional, useful later)
    df["Close Return %"] = (
        (df["Close"] - df["Prev Close"])
        / df["Prev Close"]
        * 100
    )

    # Intraday move from open
    df["Intraday Return %"] = (
        (df["Close"] - df["Open"])
        / df["Open"]
        * 100
    )

    # ==========================================================
    # ==========================================================
    # FIND ALL FAILED RECOVERIES
    # ==========================================================

    # A recovery means the day's high reached yesterday's close
    df["Recovered"] = df["High"] >= df["Prev Close"]

    # Keep ONLY failed recoveries
    failed = df[df["Recovered"] == False].copy()

    st.divider()

    st.subheader("Failed Recovery Days")

    st.write(f"Found **{len(failed)}** failed recovery days.")

    if failed.empty:
        st.warning("No failed recovery days found.")
        st.stop()
    # ==========================================================
    # RECOVERY ANALYSIS
    # ==========================================================

    # A successful recovery means the day's HIGH reached
    # or exceeded yesterday's close.

    total_days = len(df)
    total_failed = len(failed)
    total_recovered = total_days - total_failed

    failure_rate = total_failed / total_days * 100
    recovery_rate = total_recovered / total_days * 100

    total_days = len(df)
    total_failed = len(failed)
    total_recovered = total_days - total_failed

    recovery_rate = total_recovered / total_days * 100
    failure_rate = total_failed / total_days * 100

    # ==========================================================
    # SUMMARY METRICS
    # ==========================================================

    st.divider()

    st.subheader("Recovery Summary")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Trading Days",
        total_days
    )

    c2.metric(
        "Recovered",
        total_recovered
    )

    c3.metric(
        "Failed",
        total_failed
    )

    c4.metric(
        "Failure Rate",
        f"{failure_rate:.1f}%"
    )
        # ==========================================================
    # SHOW FAILED DAYS
    # ==========================================================

    st.subheader("Failed Recovery Days")

    if failed.empty:

        st.success(
            "Every matching day recovered back to the previous close."
        )

        st.stop()

        failed_display = failed[
        [
            "Date",
            "Prev Close",
            "Open",
            "High",
            "Low",
            "Close",
            "Open Move %"
        ]
        ].copy()

        failed_display["Open Move %"] = failed_display["Open Move %"].round(2)

        st.dataframe(
        failed_display,
        use_container_width=True
        )

        # Show preview
        preview = matches[
            [
                "Date",
                "Open",
                "High",
                "Low",
                "Close",
                "Prev Close",
                "Open Move %"
            ]
        ].copy()

        preview["Open Move %"] = preview["Open Move %"].round(2)

        st.dataframe(
            preview,
            use_container_width=True
        )

        # ==========================================================
    # FAILED RECOVERY ANALYSIS
    # ==========================================================

    # Maximum bounce from the OPEN
    # Example:
    # Open = 99
    # High = 99.80
    # Bounce = 0.808%

    failed["Max Bounce %"] = (
        (failed["High"] - failed["Open"])
        / failed["Open"]
        * 100
    )

    # ----------------------------------------------------------
    # Gap Recovery %
    #
    # Example:
    #
    # Prev Close = 100
    # Open = 99
    # High = 99.75
    #
    # Gap = 1.00
    # Recovery = 0.75
    #
    # Gap Recovery = 75%
    # ----------------------------------------------------------

    failed["Gap Size"] = (
        failed["Prev Close"] - failed["Open"]
    )

    failed["Gap Recovered"] = (
        failed["High"] - failed["Open"]
    )

    failed["Gap Recovery %"] = (
        failed["Gap Recovered"]
        / failed["Gap Size"]
        * 100
    )

    # Numerical safety
    failed["Gap Recovery %"] = failed["Gap Recovery %"].clip(
        lower=0,
        upper=100
    )

    # ==========================================================
    # SHOW RESULTS
    # ==========================================================

    st.divider()

    st.subheader("Failed Recovery Analysis")

    analysis = failed[
        [
            "Date",
            "Open",
            "High",
            "Prev Close",
            "Max Bounce %",
            "Gap Recovery %"
        ]
    ].copy()

    analysis["Max Bounce %"] = analysis["Max Bounce %"].round(2)
    analysis["Gap Recovery %"] = analysis["Gap Recovery %"].round(1)

    st.dataframe(
        analysis,
        use_container_width=True
    )

    # ==========================================================
    # FAILED RECOVERY STATISTICS
    # ==========================================================

    # How far below yesterday's close did the stock finish its bounce?
    failed["Miss Distance %"] = (
        (failed["Prev Close"] - failed["High"])
        / failed["Prev Close"]
        * 100
    )

    # ---------- Bounce Statistics ----------

    avg_bounce = failed["Max Bounce %"].mean()
    median_bounce = failed["Max Bounce %"].median()
    std_bounce = failed["Max Bounce %"].std()

    min_bounce = failed["Max Bounce %"].min()
    max_bounce = failed["Max Bounce %"].max()

    p25 = failed["Max Bounce %"].quantile(0.25)
    p50 = failed["Max Bounce %"].quantile(0.50)
    p75 = failed["Max Bounce %"].quantile(0.75)
    p90 = failed["Max Bounce %"].quantile(0.90)
    p95 = failed["Max Bounce %"].quantile(0.95)

    avg_gap = failed["Gap Recovery %"].mean()
    avg_miss = failed["Miss Distance %"].mean()

    # ==========================================================
    # DISPLAY
    # ==========================================================

    st.divider()

    st.subheader("Bounce Statistics")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average Bounce",
        f"{avg_bounce:.2f}%"
    )

    col2.metric(
        "Median Bounce",
        f"{median_bounce:.2f}%"
    )

    col3.metric(
        "Average Gap Recovery",
        f"{avg_gap:.1f}%"
    )

    st.write("### Distribution")

    stats = pd.DataFrame({
        "Statistic": [
            "Minimum",
            "25th Percentile",
            "Median",
            "75th Percentile",
            "90th Percentile",
            "95th Percentile",
            "Maximum",
            "Standard Deviation",
            "Average Miss Distance"
        ],
        "Value": [
            min_bounce,
            p25,
            p50,
            p75,
            p90,
            p95,
            max_bounce,
            std_bounce,
            avg_miss
        ]
    })

    stats["Value"] = stats["Value"].round(2)

    st.dataframe(
        stats,
        use_container_width=True,
        hide_index=True
    )

    # ==========================================================
    # BOUNCE PROBABILITY TABLE
    # ==========================================================

    st.divider()
    st.subheader("Bounce Probability")

    # User can change these if desired
    levels = [
        0.25,
        0.50,
        0.75,
        0.90,
        0.95,
        0.99
    ]

    probability_results = []

    for level in levels:

        probability = (
            (failed["Max Bounce %"] >= level).mean() * 100
        )

        probability_results.append({
            "Bounce Target (%)": level,
            "Probability (%)": probability
        })

    prob_df = pd.DataFrame(probability_results)

    prob_df["Probability (%)"] = prob_df["Probability (%)"].round(1)

    st.dataframe(
        prob_df,
        use_container_width=True,
        hide_index=True
    )

    # ==========================================================
    # CHARTS
    # ==========================================================

    st.divider()
    st.subheader("Charts")

    # ----------------------------------------------------------
    # Histogram of Maximum Bounce
    # ----------------------------------------------------------

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.hist(
        failed["Max Bounce %"],
        bins=15,
        edgecolor="black"
    )

    ax.set_title("Distribution of Maximum Bounce")
    ax.set_xlabel("Maximum Bounce (%)")
    ax.set_ylabel("Frequency")

    st.pyplot(fig)

    # ----------------------------------------------------------
    # Gap Recovery Histogram
    # ----------------------------------------------------------

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.hist(
        failed["Gap Recovery %"],
        bins=15,
        edgecolor="black"
    )

    ax.set_title("Distribution of Gap Recovery")
    ax.set_xlabel("Gap Recovery (%)")
    ax.set_ylabel("Frequency")

    st.pyplot(fig)

    # ----------------------------------------------------------
    # Box Plot
    # ----------------------------------------------------------

    fig, ax = plt.subplots(figsize=(8, 2))

    ax.boxplot(
        failed["Max Bounce %"],
        vert=False
    )

    ax.set_title("Maximum Bounce Box Plot")
    ax.set_xlabel("Bounce (%)")

    st.pyplot(fig)

    # ==========================================================
    # COMPLETE HISTORICAL RESULTS
    # ==========================================================

    st.divider()
    st.subheader("Historical Failed Recovery Results")

    export_df = failed.copy()

    # Keep only useful columns
    export_df = export_df[
        [
            "Date",
            "Prev Close",
            "Open",
            "High",
            "Low",
            "Close",
            "Open Move %",
            "Max Bounce %",
            "Gap Recovery %",
            "Miss Distance %"
        ]
    ].copy()

    # Round values
    numeric_cols = [
        "Prev Close",
        "Open",
        "High",
        "Low",
        "Close",
        "Open Move %",
        "Max Bounce %",
        "Gap Recovery %",
        "Miss Distance %"
    ]

    export_df[numeric_cols] = export_df[numeric_cols].round(2)

    st.dataframe(
        export_df,
        use_container_width=True,
        hide_index=True
    )

    # ==========================================================
    # DOWNLOAD CSV
    # ==========================================================

    csv = export_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download Failed Recovery Data",
        data=csv,
        file_name=f"{ticker}_failed_recovery.csv",
        mime="text/csv"
    )

    # ==========================================================
    # FINAL SUMMARY
    # ==========================================================

    st.divider()
    st.subheader("Summary")

    summary = pd.DataFrame({
        "Metric": [
            "Ticker",
            "Years",
            "Trading Days",
            "Recovered",
            "Failed",
            "Recovery Rate (%)",
            "Failure Rate (%)",
            "Average Bounce (%)",
            "Median Bounce (%)",
            "Average Gap Recovery (%)",
            "Average Miss Distance (%)"
        ],
        "Value": [
            ticker,
            years,
            total_days,
            total_recovered,
            total_failed,
            round(recovery_rate, 2),
            round(failure_rate, 2),
            round(avg_bounce, 2),
            round(median_bounce, 2),
            round(avg_gap, 2),
            round(avg_miss, 2)
    ]
})

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True
    )

    summary_csv = summary.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📊 Download Summary",
        data=summary_csv,
        file_name=f"{ticker}_summary.csv",
        mime="text/csv"
    )
