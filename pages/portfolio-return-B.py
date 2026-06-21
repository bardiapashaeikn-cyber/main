import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt
import yfinance as yf
import matplotlib.pyplot as plt

st.title("Monte Carlo Portfolio Simulator")

# Inputs
tickers_input = st.text_input(
    "Tickers (comma separated)"
)

portfolio_value = st.number_input(
    "Portfolio Value ($)",
    value=1000
)

years = st.slider(
    "Years of Historical Data",
    1,
    20,
    5
)

simulations = st.slider(
    "Number of Simulations",
    1000,
    50000,
    10000
)

if st.button("Run Simulation"):

    tickers = [x.strip().upper() for x in tickers_input.split(",")]

    end_date = dt.datetime.now()
    start_date = end_date - dt.timedelta(days=365 * years)

    prices = pd.DataFrame()

    for ticker in tickers:
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=True
        )

        if not data.empty:
            prices[ticker] = data["Close"]

    prices = prices.dropna()

    if len(prices.columns) == 0:
        st.error("No valid tickers found.")
        st.stop()

    # Daily log returns
    log_returns = np.log(prices / prices.shift(1)).dropna()

    # Equal weights
    weights = np.array(
        [1 / len(prices.columns)] * len(prices.columns)
    )

    # Historical statistics
    annual_return = (
        np.sum(log_returns.mean() * weights)
        * 252
    )

    cov_matrix = log_returns.cov() * 252

    annual_volatility = np.sqrt(
        weights.T @ cov_matrix @ weights
    )

    # Monte Carlo
    ending_values = []

    for _ in range(simulations):

        z = np.random.normal()

        simulated_return = (
            annual_return
            + annual_volatility * z
        )

        ending_value = (
            portfolio_value
            * np.exp(simulated_return)
        )

        ending_values.append(ending_value)

    ending_values = np.array(ending_values)

    # Statistics
    avg_value = np.mean(ending_values)

    median_value = np.median(ending_values)

    prob_profit = (
        (ending_values > portfolio_value)
        .mean()
        * 100
    )

    prob_loss = (
        (ending_values < portfolio_value)
        .mean()
        * 100
    )

    var_90 = np.percentile(
        ending_values,
        10
    )

    # Output
    st.subheader("Results")

    st.write(
        f"Annual Return (Historical): "
        f"{annual_return:.2%}"
    )

    st.write(
        f"Annual Volatility: "
        f"{annual_volatility:.2%}"
    )

    st.write(
        f"Average Portfolio Value: "
        f"${avg_value:,.2f}"
    )

    st.write(
        f"Median Portfolio Value: "
        f"${median_value:,.2f}"
    )

    st.write(
        f"Probability of Profit: "
        f"{prob_profit:.1f}%"
    )

    st.write(
        f"Probability of Loss: "
        f"{prob_loss:.1f}%"
    )

    st.write(
        f"10th Percentile Value (90% VaR): "
        f"${var_90:,.2f}"
    )

    # Histogram
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.hist(
        ending_values,
        bins=50
    )

    ax.axvline(
        avg_value,
        linestyle="dashed"
    )

    ax.set_title(
        "Distribution of Portfolio Value After 1 Year"
    )
    

    st.pyplot(fig)
