import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="Recovery Probability",
    layout="wide"
)

st.title("📈 Recovery Probability Analyzer")

st.write(
    """
    This tool finds historical days where a stock reached a given
    percentage move from the previous close and calculates how much
    it typically recovered before the end of the day.
    """
)

# ============================================================
# USER INPUTS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    ticker = st.text_input(
        "Ticker",
        
    ).upper()

with col2:
    current_move = st.number_input(
        "Current Move (%)",
        value=-4.00,
        step=0.25,
        format="%.2f"
    )

with col3:
    years = st.slider(
        "Years of History",
        1,
        10,
        5
    )

tolerance = st.slider(
    "Tolerance (%)",
    0.10,
    1.00,
    0.25,
    step=0.05
)

target_bounce = st.number_input(
    "Target Bounce (%)",
    value=2.00,
    step=0.25,
    format="%.2f"
)

# ============================================================
# DOWNLOAD DATA
# ============================================================

if st.button("Analyze"):

    with st.spinner("Downloading historical data..."):

        try:

            df = yf.download(
                ticker,
                period=f"{years}y",
                progress=False,
                auto_adjust=False
            )

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

        except Exception as e:

            st.error(e)
            st.stop()

    if df.empty:

        st.error("No data found.")
        st.stop()

    # ========================================================
    # PREPARE DATA
    # ========================================================

    df = df[["Open", "High", "Low", "Close"]].copy()

    df["Prev Close"] = df["Close"].shift(1)

    df.dropna(inplace=True)

    # --------------------------------------------------------
    # Percentage moves from previous close
    # --------------------------------------------------------

    df["Open %"] = (
        (df["Open"] - df["Prev Close"])
        / df["Prev Close"]
    ) * 100

    df["High %"] = (
        (df["High"] - df["Prev Close"])
        / df["Prev Close"]
    ) * 100

    df["Low %"] = (
        (df["Low"] - df["Prev Close"])
        / df["Prev Close"]
    ) * 100

    df["Close %"] = (
        (df["Close"] - df["Prev Close"])
        / df["Prev Close"]
    ) * 100

    # ========================================================
    # FIND MATCHING DAYS
    # ========================================================

    if current_move < 0:

            # Stock reached or exceeded the downside threshold
        matches = df[
            df["Low %"] <= current_move
        ].copy()

    else:

    # Stock reached or exceeded the upside threshold
        matches = df[
            df["High %"] >= current_move
        ].copy()

    st.divider()

    st.subheader("Matching Days")

    st.write(f"Historical Matches Found: **{len(matches)}**")

    if len(matches) == 0:

        st.warning("No matching days were found.")

        st.stop()

    # ========================================================
    # RECOVERY ANALYSIS
    # ========================================================

    results = []

    hits = 0

    for date, row in matches.iterrows():

        # -------------------------
        # Bounce Calculation
        # -------------------------

        if current_move < 0:

            # Bounce from day's low to day's high
            bounce = (
                (row["High"] - row["Low"])
                / row["Low"]
            ) * 100

        else:

            # Pullback from day's high to day's low
            bounce = (
                (row["Low"] - row["High"])
                / row["High"]
            ) * 100

            bounce = abs(bounce)

        hit = bounce >= target_bounce

        if hit:
            hits += 1

        results.append({

            "Date": date,

            "Previous Close": row["Prev Close"],

            "Open %": row["Open %"],

            "High %": row["High %"],

            "Low %": row["Low %"],

            "Close %": row["Close %"],

            "Bounce %": bounce,

            "Hit": "✅" if hit else "❌"

        })

        # ========================================================
        # RESULTS DATAFRAME
        # ========================================================

    results_df = pd.DataFrame(results)

    probability = hits / len(results_df) * 100

    average_bounce = results_df["Bounce %"].mean()

    median_bounce = results_df["Bounce %"].median()

    best_bounce = results_df["Bounce %"].max()

    worst_bounce = results_df["Bounce %"].min()

    # ========================================================
    # METRICS
    # ========================================================

    st.divider()

    st.subheader("Recovery Statistics")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Matches",
        len(results_df)
    )

    c2.metric(
        "Hits",
        hits
    )

    c3.metric(
        "Probability",
        f"{probability:.1f}%"
    )

    c4.metric(
        "Average Bounce",
        f"{average_bounce:.2f}%"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Median Bounce",
        f"{median_bounce:.2f}%"
    )

    c2.metric(
        "Best Bounce",
        f"{best_bounce:.2f}%"
    )

    c3.metric(
        "Worst Bounce",
        f"{worst_bounce:.2f}%"
    )

    # ========================================================
    # MATCHING DAYS TABLE
    # ========================================================

    st.divider()

    st.subheader("Historical Matches")

    results_df = results_df.round(2)

    st.dataframe(
        results_df,
        use_container_width=True
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    st.success(

        f"""
    Out of **{len(results_df)}** historical trading days that reached reached {current_move:.2f}% or beyond**,

    the stock moved at least **{target_bounce:.2f}%**

    on **{hits}** days.

    Estimated Probability:

    # {probability:.1f}%
    """
    )

    # ========================================================
    # PROBABILITY TABLE
    # ========================================================

    st.divider()

    st.subheader("Probability Table")

    targets = np.arange(0.5, 5.5, 0.5)

    table = []

    for target in targets:

        hit_count = (results_df["Bounce %"] >= target).sum()

        probability = hit_count / len(results_df) * 100

        table.append({

            "Target Bounce %": round(target, 2),

            "Probability %": round(probability, 2),

            "Hits": int(hit_count)

        })

    probability_df = pd.DataFrame(table)

    st.dataframe(
        probability_df,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # BEST HISTORICAL DAYS
    # ========================================================

    st.divider()

    st.subheader("Top Recoveries")

    top = results_df.sort_values(
        "Bounce %",
        ascending=False
    ).head(10)

    st.dataframe(
        top,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # WORST HISTORICAL DAYS
    # ========================================================

    st.subheader("Smallest Recoveries")

    worst = results_df.sort_values(
        "Bounce %",
        ascending=True
    ).head(10)

    st.dataframe(
        worst,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # DOWNLOAD RESULTS
    # ========================================================

    csv = results_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download Historical Results",
        data=csv,
        file_name=f"{ticker}_Recovery_Analysis.csv",
        mime="text/csv"
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    st.divider()

    st.info(
        f"""
    Ticker: {ticker}

    Current Move: {current_move:.2f}%

    Tolerance: ±{tolerance:.2f}%

    Historical Matches: {len(results_df)}

    Average Bounce: {average_bounce:.2f}%

    Estimated Probability of at least {target_bounce:.2f}% bounce:

    {probability:.1f}%
    """
    )
