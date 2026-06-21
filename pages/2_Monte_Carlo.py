import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import datetime as dt

st.set_page_config(
    page_title="Monte Carlo Stock Forecast",
    layout="centered"
)

st.title("Monte Carlo Stock Forecast")

# -----------------------------
# USER INPUTS
# -----------------------------

ticker = st.text_input(
    "Ticker",
    value=""
)

history_years = st.number_input(
    "Years of Historical Data",
    min_value=1,
    max_value=20,
    value=5
)

forecast_years = st.number_input(
    "Years to Forecast",
    min_value=1,
    max_value=10,
    value=1
)

simulations = st.number_input(
    "Number of Simulations",
    min_value=100,
    max_value=50000,
    value=10000,
    step=100
)

# -----------------------------
# RUN BUTTON
# -----------------------------

if st.button("Run Simulation"):

    if ticker == "":
        st.warning("Please enter a ticker.")
        st.stop()

    end_date = dt.datetime.now()

    start_date = (
        end_date -
        dt.timedelta(days=365 * history_years)
    )

    data = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        auto_adjust=True
    )

    if data.empty:
        st.error("No data found.")
        st.stop()

    prices = data["Close"]

    st.subheader("Historical Price")

    fig1, ax1 = plt.subplots(figsize=(10,5))
    ax1.plot(prices)
    ax1.set_title(f"{ticker.upper()} Historical Price")
    ax1.set_ylabel("Price")
    st.pyplot(fig1)

    # -----------------------------
    # RETURNS
    # -----------------------------

    log_returns = np.log(
        prices / prices.shift(1)
    ).dropna()

    mu = log_returns.mean().item()
    sigma = log_returns.std().item()

    forecast_days = int(
        forecast_years * 252
    )

    current_price = prices.iloc[-1].item()
    
    paths = np.zeros(
        (forecast_days, simulations)
    )

    paths[0] = current_price

    # -----------------------------
    # MONTE CARLO
    # -----------------------------

    for sim in range(simulations):

        for day in range(1, forecast_days):

            shock = np.random.normal(
                mu,
                sigma
            )

            paths[day, sim] = (
                paths[day - 1, sim]
                * np.exp(shock)
            )

    # -----------------------------
    # STATISTICS
    # -----------------------------

    median_path = np.percentile(
        paths,
        50,
        axis=1
    )

    p10 = np.percentile(
        paths,
        10,
        axis=1
    )

    p90 = np.percentile(
        paths,
        90,
        axis=1
    )

    final_prices = paths[-1]

    # -----------------------------
    # FORECAST CHART
    # -----------------------------

    # -----------------------------
# FORECAST CHART
# -----------------------------

     # -----------------------------
    # FORECAST CHART
    # -----------------------------

    st.subheader(
        f"Forecast ({forecast_years} Years)"
    )

    fig2, ax2 = plt.subplots(figsize=(8,4))

    # Plot only 30 simulated paths
    for i in range(min(30, simulations)):
        ax2.plot(
            paths[:, i],
            alpha=0.1
        )

    # Keep extreme outliers from stretching chart
    ax2.set_ylim(
        0,
        np.percentile(paths[-1], 95)
    )

    ax2.plot(
        median_path,
        linewidth=3,
        label="Most Likely Path"
    )

    ax2.plot(
        p10,
        linestyle="--",
        label="10th Percentile"
    )

    ax2.plot(
        p90,
        linestyle="--",
        label="90th Percentile"
    )

    ax2.set_title(
        f"{ticker.upper()} Monte Carlo Forecast"
    )

    ax2.set_xlabel(
        "Trading Days"
    )

    ax2.set_ylabel(
        "Price"
    )

    ax2.legend()

    st.pyplot(fig2)
    # -----------------------------
    # RESULTS
    # -----------------------------

    st.subheader("Results")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Current Price",
        f"${current_price:,.2f}"
    )

    col2.metric(
        "Median Future Price",
        f"${np.median(final_prices):,.2f}"
    )

    col3.metric(
        "10th Percentile",
        f"${np.percentile(final_prices,10):,.2f}"
    )

    col4.metric(
        "90th Percentile",
        f"${np.percentile(final_prices,90):,.2f}"
    )

    up_probability = (
        np.sum(
            final_prices > current_price
        )
        / simulations
    ) * 100

    down_probability = (
        np.sum(
            final_prices < current_price
        )
        / simulations
    ) * 100

    st.write(
        f"Probability price ends ABOVE current price: "
        f"**{up_probability:.2f}%**"
    )

    st.write(
        f"Probability price ends BELOW current price: "
        f"**{down_probability:.2f}%**"
    )
