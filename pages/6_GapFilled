import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Gap Fill Probability Analyzer",
    layout="wide"
)

st.title("📈 Gap Fill Probability Analyzer")

st.markdown("""
Analyze the probability that a stock fills its opening gap during the same trading day.

A **Gap Down** is considered filled if:

Today's High >= Yesterday's Close

A **Gap Up** is considered filled if:

Today's Low <= Yesterday's Close
""")

# ----------------------------------------------------
# Sidebar Inputs
# ----------------------------------------------------

st.sidebar.header("Inputs")

ticker_input = st.sidebar.text_area(
    "Tickers (comma separated)",
    value="AAPL,MSFT,NVDA"
)

start_date = st.sidebar.date_input(
    "Start Date",
    pd.to_datetime("2018-01-01")
)

end_date = st.sidebar.date_input(
    "End Date",
    pd.Timestamp.today()
)

gap_direction = st.sidebar.selectbox(
    "Gap Direction",
    [
        "Gap Down",
        "Gap Up",
        "Both"
    ]
)

st.sidebar.markdown("---")

gap_min = st.sidebar.number_input(
    "Minimum Gap (%)",
    value=-2.0,
    step=0.1,
    format="%.2f"
)

gap_max = st.sidebar.number_input(
    "Maximum Gap (%)",
    value=-1.0,
    step=0.1,
    format="%.2f"
)

run_button = st.sidebar.button("Analyze")


# ----------------------------------------------------
# Helper Function
# ----------------------------------------------------

def download_data(ticker):

    df = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        auto_adjust=False,
        progress=False
    )

    if df.empty:
        return None

    # Flatten MultiIndex if necessary
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df[["Open", "High", "Low", "Close"]].copy()

    df = df.astype(float)

    df.dropna(inplace=True)

    return df


# ----------------------------------------------------
# Gap Analysis
# ----------------------------------------------------

def analyze_gap(df, ticker):

    rows = []

    for i in range(1, len(df)):

        prev_close = df["Close"].iloc[i-1]

        today_open = df["Open"].iloc[i]

        today_high = df["High"].iloc[i]

        today_low = df["Low"].iloc[i]

        today_close = df["Close"].iloc[i]

        date = df.index[i]

        gap_pct = (today_open - prev_close) / prev_close * 100

        gap_type = ""

        filled = False

        if gap_pct < 0:

            gap_type = "Gap Down"

            if today_high >= prev_close:
                filled = True

        elif gap_pct > 0:

            gap_type = "Gap Up"

            if today_low <= prev_close:
                filled = True

        else:
            continue

        keep = False

        if gap_direction == "Gap Down":

            if gap_type == "Gap Down":

                if gap_min <= gap_pct <= gap_max:
                    keep = True

        elif gap_direction == "Gap Up":

            if gap_type == "Gap Up":

                if gap_min <= gap_pct <= gap_max:
                    keep = True

        else:

            if gap_min <= gap_pct <= gap_max:
                keep = True

        if keep:

            rows.append(
                {
                    "Ticker": ticker,
                    "Date": date,
                    "Gap Type": gap_type,
                    "Previous Close": prev_close,
                    "Open": today_open,
                    "High": today_high,
                    "Low": today_low,
                    "Close": today_close,
                    "Gap %": gap_pct,
                    "Filled": filled
                }
            )

    return pd.DataFrame(rows)


# ----------------------------------------------------
# Main
# ----------------------------------------------------

if run_button:

    tickers = [
        x.strip().upper()
        for x in ticker_input.split(",")
        if x.strip()
    ]

    all_results = []

    progress = st.progress(0)

    status = st.empty()

    for idx, ticker in enumerate(tickers):

        status.write(f"Downloading {ticker}...")

        df = download_data(ticker)

        if df is None:
            continue

        result = analyze_gap(df, ticker)

        if not result.empty:
            all_results.append(result)

        progress.progress((idx + 1) / len(tickers))

    status.empty()

    if len(all_results) == 0:

        st.warning("No matching gaps found.")

        st.stop()

    results = pd.concat(all_results)

    results.reset_index(drop=True, inplace=True)
    
        # ------------------------------------------------
    # Summary Statistics
    # ------------------------------------------------

    total_gaps = len(results)

    filled_gaps = results["Filled"].sum()

    fill_rate = (filled_gaps / total_gaps) * 100

    avg_gap = results["Gap %"].mean()

    avg_abs_gap = results["Gap %"].abs().mean()

    st.markdown("## Overall Statistics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Gaps",
        f"{total_gaps:,}"
    )

    col2.metric(
        "Filled Gaps",
        f"{filled_gaps:,}"
    )

    col3.metric(
        "Fill Probability",
        f"{fill_rate:.2f}%"
    )

    col4.metric(
        "Average Gap",
        f"{avg_gap:.2f}%"
    )

    st.markdown("---")

    # ------------------------------------------------
    # Per-Ticker Statistics
    # ------------------------------------------------

    summary = (
        results
        .groupby("Ticker")
        .agg(
            Total_Gaps=("Filled", "count"),
            Filled_Gaps=("Filled", "sum"),
            Average_Gap=("Gap %", "mean")
        )
    )

    summary["Fill %"] = (
        summary["Filled_Gaps"]
        / summary["Total_Gaps"]
        * 100
    )

    summary = summary.sort_values(
        "Fill %",
        ascending=False
    )

    st.subheader("Ticker Statistics")

    st.dataframe(
        summary.style.format({
            "Average_Gap": "{:.2f}%",
            "Fill %": "{:.2f}%"
        }),
        use_container_width=True
    )

    st.markdown("---")

    # ------------------------------------------------
    # Weekday Analysis
    # ------------------------------------------------

    weekday = results.copy()

    weekday["Weekday"] = pd.to_datetime(
        weekday["Date"]
    ).dt.day_name()

    weekday_stats = (
        weekday
        .groupby("Weekday")
        .agg(
            Total=("Filled", "count"),
            Filled=("Filled", "sum")
        )
    )

    weekday_stats["Fill %"] = (
        weekday_stats["Filled"]
        / weekday_stats["Total"]
        * 100
    )

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday"
    ]

    weekday_stats = weekday_stats.reindex(
        weekday_order
    )

    st.subheader("Weekday Statistics")

    st.dataframe(
        weekday_stats.style.format({
            "Fill %": "{:.2f}%"
        }),
        use_container_width=True
    )

    st.markdown("---")

    # ------------------------------------------------
    # Gap Size Statistics
    # ------------------------------------------------

    st.subheader("Gap Statistics")

    gap_stats = pd.DataFrame({
        "Statistic": [
            "Smallest Gap",
            "Largest Gap",
            "Average Gap",
            "Median Gap",
            "Std Dev"
        ],
        "Value": [
            results["Gap %"].min(),
            results["Gap %"].max(),
            results["Gap %"].mean(),
            results["Gap %"].median(),
            results["Gap %"].std()
        ]
    })

    gap_stats["Value"] = gap_stats["Value"].map(
        lambda x: f"{x:.2f}%"
    )

    st.table(gap_stats)

    st.markdown("---")

    # ------------------------------------------------
    # Filled vs Not Filled
    # ------------------------------------------------

    filled_table = pd.DataFrame({
        "Result": [
            "Filled",
            "Not Filled"
        ],
        "Count": [
            filled_gaps,
            total_gaps - filled_gaps
        ]
    })

    st.subheader("Fill Results")

    st.dataframe(
        filled_table,
        use_container_width=True
    )

    st.markdown("---")


        # ------------------------------------------------
    # Charts
    # ------------------------------------------------

    st.header("Charts")

    col1, col2 = st.columns(2)

    # Pie Chart
    with col1:

        fig, ax = plt.subplots(figsize=(5,5))

        ax.pie(
            [
                filled_gaps,
                total_gaps-filled_gaps
            ],
            labels=[
                "Filled",
                "Not Filled"
            ],
            autopct="%1.1f%%",
            startangle=90
        )

        ax.set_title("Gap Fill Results")

        st.pyplot(fig)

    # Histogram
    with col2:

        fig, ax = plt.subplots(figsize=(6,5))

        ax.hist(
            results["Gap %"],
            bins=20
        )

        ax.set_title("Gap Size Distribution")

        ax.set_xlabel("Gap %")

        ax.set_ylabel("Count")

        st.pyplot(fig)

    st.markdown("---")

    # ------------------------------------------------
    # Weekday Chart
    # ------------------------------------------------

    st.subheader("Gap Fill Probability by Weekday")

    fig, ax = plt.subplots(figsize=(8,4))

    ax.bar(
        weekday_stats.index,
        weekday_stats["Fill %"]
    )

    ax.set_ylabel("Fill %")

    ax.set_ylim(0,100)

    plt.xticks(rotation=30)

    st.pyplot(fig)

    st.markdown("---")

    # ------------------------------------------------
    # Top Performing Tickers
    # ------------------------------------------------

    st.subheader("Highest Gap Fill Probability")

    top = summary.sort_values(
        "Fill %",
        ascending=False
    )

    st.dataframe(
        top.head(15).style.format({
            "Fill %":"{:.2f}%",
            "Average_Gap":"{:.2f}%"
        }),
        use_container_width=True
    )

    st.markdown("---")

    # ------------------------------------------------
    # Lowest Fill Probability
    # ------------------------------------------------

    st.subheader("Lowest Gap Fill Probability")

    bottom = summary.sort_values(
        "Fill %",
        ascending=True
    )

    st.dataframe(
        bottom.head(15).style.format({
            "Fill %":"{:.2f}%",
            "Average_Gap":"{:.2f}%"
        }),
        use_container_width=True
    )

    st.markdown("---")

    # ------------------------------------------------
    # Detailed Results
    # ------------------------------------------------

    st.subheader("Every Matching Gap")

    display = results.copy()

    display["Date"] = pd.to_datetime(
        display["Date"]
    ).dt.strftime("%Y-%m-%d")

    display["Gap %"] = display["Gap %"].round(2)

    st.dataframe(
        display,
        use_container_width=True,
        height=600
    )

    st.markdown("---")

    # ------------------------------------------------
    # Download Button
    # ------------------------------------------------

    csv = display.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name="gap_fill_results.csv",
        mime="text/csv"
    )

    st.success("Analysis Complete!")
