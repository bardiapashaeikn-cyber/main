import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import coint
import statsmodels.api as sm

st.set_page_config(layout="wide")

st.title("📈 Pairs Trading Analyzer (Clean UI)")

# -----------------------
# CENTERED CONTAINER
# -----------------------

with st.container():
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 900px;
            margin: auto;
        }

        .stApp {
            background-color: "White";
        }

        .input-box {
            background-color: #1c1f26;
            padding: 20px;
            border-radius: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 🎯 Pair Selection Panel")

    col1, col2 = st.columns(2)

    with col1:
        ticker1 = st.text_input("Ticker 1", "KO")

    with col2:
        ticker2 = st.text_input("Ticker 2", "PEP")

    period = st.selectbox(
        "History",
        ["1y", "2y", "5y", "10y"],
        index=2
    )

# -----------------------
# DATA
# -----------------------

data1 = yf.download(ticker1, period=period)["Close"]
data2 = yf.download(ticker2, period=period)["Close"]

df = pd.concat([data1, data2], axis=1)
df.columns = [ticker1, ticker2]
df = df.dropna()

if df.empty or len(df) < 50:
    st.error("Not enough data")
    st.stop()

# -----------------------
# ANALYSIS
# -----------------------

score, pvalue, _ = coint(df[ticker1], df[ticker2])

correlation = df[ticker1].corr(df[ticker2])

X = sm.add_constant(df[ticker2])
model = sm.OLS(df[ticker1], X).fit()

beta = model.params[df.columns[1]]

spread = df[ticker1] - beta * df[ticker2]
zscore = (spread - spread.mean()) / spread.std()

current_z = zscore.iloc[-1]

# -----------------------
# FILTER
# -----------------------

is_valid_pair = (pvalue < 0.05) and (abs(correlation) > 0.7)

if not is_valid_pair:
    signal = "❌ NOT A VALID PAIRS TRADING RELATIONSHIP"
else:
    if current_z > 2:
        signal = f"🔴 SHORT {ticker1} / LONG {ticker2}"
    elif current_z < -2:
        signal = f"🟢 LONG {ticker1} / SHORT {ticker2}"
    else:
        signal = "⚪ NO SIGNAL"

# -----------------------
# METRICS
# -----------------------

st.markdown("### 📊 Metrics")

c1, c2, c3, c4 = st.columns(4)

c1.metric("p-value", f"{pvalue:.4f}")
c2.metric("Correlation", f"{correlation:.2f}")
c3.metric("Beta", f"{beta:.2f}")
c4.metric("Z-Score", f"{current_z:.2f}")

st.markdown("### ⚡ Signal")
st.success(signal)

# -----------------------
# SMALLER CHARTS
# -----------------------

st.markdown("### 📉 Spread")

fig, ax = plt.subplots(figsize=(6, 2.5))
ax.plot(spread)
ax.axhline(spread.mean(), linestyle="--")
ax.set_title("Spread")
st.pyplot(fig)

st.markdown("### 📈 Z-Score")

fig, ax = plt.subplots(figsize=(6, 2.5))
ax.plot(zscore)
ax.axhline(2, color="red", linestyle="--")
ax.axhline(-2, color="green", linestyle="--")
ax.axhline(0, color="Black")
ax.set_title("Z-Score")
st.pyplot(fig)
