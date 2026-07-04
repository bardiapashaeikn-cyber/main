import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------
# Page Setup
# -------------------------------------------------------

st.set_page_config(
    page_title="Next Day Probability Engine",
    layout="wide"
)

st.title("📈 Next Day Probability Engine")
st.write(
    "Find what historically happened the day after a stock moved a certain percentage."
)

# -------------------------------------------------------
# Sidebar
# -------------------------------------------------------

st.sidebar.header("Settings")

ticker = st.sidebar.text_input(
    "Ticker",
    value="NFLX"
).upper()

start_date = st.sidebar.date_input(
    "Start Date",
    value=pd.to_datetime("2015-01-01")
)

end_date = st.sidebar.date_input(
    "End Date",
    value=pd.Timestamp.today()
)

today_move = st.sidebar.number_input(
    "Today's Move (%)",
    value=2.00,
    step=0.10,
    format="%.2f"
)

tolerance = st.sidebar.slider(
    "Tolerance (%)",
    min_value=0.05,
    max_value=2.00,
    value=0.25,
    step=0.05
)

direction = st.sidebar.selectbox(
    "Direction",
    [
        "Any",
        "Green Only",
        "Red Only"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Indicator Filters")

use_rsi = st.sidebar.checkbox("Use RSI Filter")

if use_rsi:
    rsi_min = st.sidebar.slider(
        "Minimum RSI",
        0,
        100,
        40
    )

    rsi_max = st.sidebar.slider(
        "Maximum RSI",
        0,
        100,
        60
    )

use_volume = st.sidebar.checkbox("High Volume Only")

volume_multiplier = st.sidebar.slider(
    "Volume > Average ×",
    1.0,
    5.0,
    1.5,
    0.1
)

use_ma = st.sidebar.checkbox("Only Above 50 MA")

run = st.sidebar.button("Analyze")

# -------------------------------------------------------
# Download Data
# -------------------------------------------------------

if run:

    with st.spinner("Downloading data..."):

        df = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            auto_adjust=True,
            progress=False
        )

        # Flatten MultiIndex columns if necessary
    if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

    if df.empty:

        st.error("No data found.")
        st.stop()

    # ------------------------------------------
    # Daily Return (%)
    # ------------------------------------------

    df["Today Return %"] = (
        df["Close"].pct_change() * 100
    )

    # Tomorrow Return

    df["Tomorrow Return %"] = (
        df["Today Return %"].shift(-1)
    )
    
    # -------------------------------------------------------
    # Indicators
    # -------------------------------------------------------

    # RSI (14)

    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    df["RSI"] = 100 - (100 / (1 + rs))

    # Moving Averages

    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()

    # Average Volume

    df["AvgVolume20"] = df["Volume"].rolling(20).mean()

    df.dropna(inplace=True)

    # ------------------------------------------
    # Range Filter
    # ------------------------------------------

    lower = today_move - tolerance
    upper = today_move + tolerance

    if direction == "Green Only":

        matches = df[
            (df["Today Return %"] >= lower) &
            (df["Today Return %"] <= upper) &
            (df["Today Return %"] > 0)
        ]

    elif direction == "Red Only":

        matches = df[
            (df["Today Return %"] >= lower) &
            (df["Today Return %"] <= upper) &
            (df["Today Return %"] < 0)
        ]

    else:

        matches = df[
            (df["Today Return %"] >= lower) &
            (df["Today Return %"] <= upper)
        ]

    


    # -------------------------------------------------------
# Apply Indicator Filters
# -------------------------------------------------------

    if use_rsi:
        matches = matches[
            (matches["RSI"] >= rsi_min) &
            (matches["RSI"] <= rsi_max)
        ]

    if use_volume:
        matches = matches[
            matches["Volume"] >
            matches["AvgVolume20"] * volume_multiplier
        ]

    if use_ma:
        matches = matches[
            matches["Close"] >
            matches["MA50"]
        ]

    # -------------------------------------------------------
# Statistics
# -------------------------------------------------------
    st.success(f"Found {len(matches)} historical matches.")
    
    if len(matches) == 0:
        st.warning("No historical matches found.")
        st.stop()

    tomorrow = matches["Tomorrow Return %"]

    green = (tomorrow > 0).sum()
    red = (tomorrow < 0).sum()

    green_pct = green / len(matches) * 100
    red_pct = red / len(matches) * 100

    avg_return = tomorrow.mean()
    median_return = tomorrow.median()
    std_return = tomorrow.std()

    best_return = tomorrow.max()
    worst_return = tomorrow.min()

    above1 = (tomorrow > 1).mean() * 100
    above2 = (tomorrow > 2).mean() * 100

    below1 = (tomorrow < -1).mean() * 100
    below2 = (tomorrow < -2).mean() * 100

    # -------------------------------------------------------
    # Display Statistics
    # -------------------------------------------------------

    st.markdown("## Historical Results")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Occurrences",
            len(matches)
        )

    with col2:
        st.metric(
            "Tomorrow Green",
            f"{green_pct:.1f}%"
        )

    with col3:
        st.metric(
            "Tomorrow Red",
            f"{red_pct:.1f}%"
        )

    with col4:
        st.metric(
            "Average Return",
            f"{avg_return:.2f}%"
        )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Median Return",
            f"{median_return:.2f}%"
        )

        st.metric(
            "Standard Deviation",
            f"{std_return:.2f}%"
        )

    with col2:
        st.metric(
            "Best Next Day",
            f"{best_return:.2f}%"
        )

        st.metric(
            "Worst Next Day",
            f"{worst_return:.2f}%"
        )

    with col3:
        st.metric(
            "Chance > +1%",
            f"{above1:.1f}%"
        )

        st.metric(
            "Chance > +2%",
            f"{above2:.1f}%"
        )

        st.metric(
            "Chance < -1%",
            f"{below1:.1f}%"
        )

        st.metric(
            "Chance < -2%",
            f"{below2:.1f}%"
        )



        # -------------------------------------------------------
    # Histogram
    # -------------------------------------------------------

    st.markdown("---")
    st.subheader("Distribution of Tomorrow's Returns")

    fig, ax = plt.subplots(figsize=(10,5))

    ax.hist(
        tomorrow,
        bins=25
    )

    ax.set_xlabel("Tomorrow Return (%)")
    ax.set_ylabel("Frequency")
    ax.set_title("Historical Distribution")

    st.pyplot(fig)

    # -------------------------------------------------------
    # Summary Table
    # -------------------------------------------------------

    st.markdown("---")
    st.subheader("Historical Matches")

    display = matches.copy()

    display = display[[
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "Today Return %",
        "Tomorrow Return %"
    ]]

    display = display.round(2)

    st.dataframe(
        display,
        use_container_width=True
    )

    # -------------------------------------------------------
    # Download CSV
    # -------------------------------------------------------

    csv = display.to_csv().encode("utf-8")

    st.download_button(
        label="📥 Download Historical Matches",
        data=csv,
        file_name=f"{ticker}_historical_matches.csv",
        mime="text/csv"
    )

    # -------------------------------------------------------
    # Extra Statistics
    # -------------------------------------------------------

    st.markdown("---")
    st.subheader("Next Day Return Percentiles")

    percentiles = pd.DataFrame({
        "Percentile":[
            "10%",
            "25%",
            "50%",
            "75%",
            "90%"
        ],
        "Tomorrow Return (%)":[
            tomorrow.quantile(.10),
            tomorrow.quantile(.25),
            tomorrow.quantile(.50),
            tomorrow.quantile(.75),
            tomorrow.quantile(.90)
        ]
    })

    percentiles = percentiles.round(2)

    st.table(percentiles)

    # -------------------------------------------------------
    # Expected Price
    # -------------------------------------------------------

    st.markdown("---")
    st.subheader("Expected Tomorrow Price")

    last_close = float(df["Close"].values[-1])

    expected_price = last_close * (1 + avg_return/100)

    col1,col2 = st.columns(2)

    with col1:
        st.metric(
            "Latest Close",
            f"${last_close:.2f}"
        )

    with col2:
        st.metric(
            "Expected Price",
            f"${expected_price:.2f}"
        )


        # -------------------------------------------------------
    # Simulated Trading Performance
    # -------------------------------------------------------

    st.markdown("---")
    st.subheader("📈 Strategy Performance")

    # Assume buying at today's close and selling at tomorrow's close
    equity = (1 + tomorrow / 100).cumprod()

    fig2, ax2 = plt.subplots(figsize=(10,5))

    ax2.plot(
        equity.values,
        linewidth=2
    )

    ax2.set_title("Growth of $1 if Every Signal Was Traded")
    ax2.set_xlabel("Trade Number")
    ax2.set_ylabel("Portfolio Value")

    st.pyplot(fig2)

    # -------------------------------------------------------
    # Win / Loss Statistics
    # -------------------------------------------------------

    wins = tomorrow[tomorrow > 0]
    losses = tomorrow[tomorrow < 0]

    win_rate = len(wins) / len(tomorrow) * 100

    loss_rate = len(losses) / len(tomorrow) * 100

    avg_win = wins.mean() if len(wins) else 0
    avg_loss = losses.mean() if len(losses) else 0

    profit_factor = (
        wins.sum() /
        abs(losses.sum())
        if losses.sum() != 0
        else np.nan
    )

    col1,col2,col3,col4 = st.columns(4)

    with col1:
        st.metric("Win Rate", f"{win_rate:.1f}%")

    with col2:
        st.metric("Average Win", f"{avg_win:.2f}%")

    with col3:
        st.metric("Average Loss", f"{avg_loss:.2f}%")

    with col4:
        st.metric("Profit Factor", f"{profit_factor:.2f}")

    # -------------------------------------------------------
    # Expectancy
    # -------------------------------------------------------

    expectancy = (
        (win_rate/100)*avg_win +
        (loss_rate/100)*avg_loss
    )

    st.metric(
        "Expectancy Per Trade",
        f"{expectancy:.2f}%"
    )

    # -------------------------------------------------------
    # Sample Size Confidence
    # -------------------------------------------------------

    sample = len(matches)

    if sample < 20:
        confidence = "🔴 Low"

    elif sample < 75:
        confidence = "🟡 Medium"

    else:
        confidence = "🟢 High"

    st.metric(
        "Confidence",
        confidence
    )

    # -------------------------------------------------------
    # Future Returns
    # -------------------------------------------------------

    future = df.copy()

    future["5 Day Return %"] = (
        future["Close"].shift(-5) /
        future["Close"] - 1
    ) * 100

    future["10 Day Return %"] = (
        future["Close"].shift(-10) /
        future["Close"] - 1
    ) * 100

    future_matches = future.loc[matches.index]

    avg5 = future_matches["5 Day Return %"].mean()
    avg10 = future_matches["10 Day Return %"].mean()

    col1,col2 = st.columns(2)

    with col1:
        st.metric(
            "Average 5-Day Return",
            f"{avg5:.2f}%"
        )

    with col2:
        st.metric(
            "Average 10-Day Return",
            f"{avg10:.2f}%"
        )

    # -------------------------------------------------------
    # Scatter Plot
    # -------------------------------------------------------

    st.markdown("---")
    st.subheader("Today's Move vs Tomorrow's Move")

    fig3, ax3 = plt.subplots(figsize=(8,6))

    ax3.scatter(
        matches["Today Return %"],
        matches["Tomorrow Return %"]
    )

    ax3.set_xlabel("Today's Return (%)")
    ax3.set_ylabel("Tomorrow's Return (%)")
    ax3.set_title("Historical Relationship")

    st.pyplot(fig3)
