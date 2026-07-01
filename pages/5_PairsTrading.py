import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import coint
import statsmodels.api as sm

st.set_page_config(layout="wide")

st.title("📈 Pairs Trading Analyzer")

# -----------------------
# Inputs
# -----------------------

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
# Download Data
# -----------------------

data1 = yf.download(ticker1, period=period)["Close"]
data2 = yf.download(ticker2, period=period)["Close"]

df = pd.concat([data1, data2], axis=1)
df.columns = [ticker1, ticker2]
df = df.dropna()

# -----------------------
# Cointegration Test
# -----------------------

score, pvalue, _ = coint(df[ticker1], df[ticker2])

# -----------------------
# Hedge Ratio
# -----------------------

X = sm.add_constant(df[ticker2])
model = sm.OLS(df[ticker1], X).fit()

beta = model.params[ticker2]

# -----------------------
# Spread
# -----------------------

spread = df[ticker1] - beta * df[ticker2]

# -----------------------
# Z Score
# -----------------------

zscore = (
    spread - spread.mean()
) / spread.std()

current_z = zscore.iloc[-1]

# -----------------------
# Signal
# -----------------------

if current_z > 2:
    signal = f"🔴 SHORT {ticker1} / LONG {ticker2}"

elif current_z < -2:
    signal = f"🟢 LONG {ticker1} / SHORT {ticker2}"

else:
    signal = "⚪ NO SIGNAL"

# -----------------------
# Metrics
# -----------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric("Cointegration p-value", f"{pvalue:.4f}")
c2.metric("Correlation", f"{df[ticker1].corr(df[ticker2]):.2f}")
c3.metric("Beta", f"{beta:.2f}")
c4.metric("Current Z-Score", f"{current_z:.2f}")

st.subheader("Trading Signal")
st.success(signal)

# -----------------------
# Spread Chart
# -----------------------

fig, ax = plt.subplots(figsize=(10,4))

ax.plot(spread)

ax.axhline(
    spread.mean(),
    linestyle="--",
    label="Mean"
)

ax.set_title("Spread")

ax.legend()

st.pyplot(fig)

# -----------------------
# Z-Score Chart
# -----------------------

fig, ax = plt.subplots(figsize=(10,4))

ax.plot(zscore)

ax.axhline(2, color="red", linestyle="--")
ax.axhline(-2, color="green", linestyle="--")
ax.axhline(0, color="black")

ax.set_title("Z-Score")

st.pyplot(fig)
