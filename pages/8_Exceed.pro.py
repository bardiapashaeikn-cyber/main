import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =====================================================
# INDUSTRY PEERS
# =====================================================

industry_peers = {

    "Semiconductors": [
        "NVDA","AVGO","AMD","QCOM","TXN",
        "MU","ADI","INTC","MCHP","ON"
    ],

    "Drug Manufacturers - General": [
        "LLY","JNJ","ABBV","MRK","PFE",
        "BMY","AMGN","GILD","VRTX","REGN"
    ],

    "Biotechnology": [
        "VRTX","REGN","GILD","AMGN",
        "SRPT","MRNA","BIIB","BNTX",
        "EXEL","ALNY"
    ],

    "Software - Application": [
        "CRM","NOW","ADBE","INTU","SNOW",
        "DOCU","TEAM","DDOG","HUBS","SHOP"
    ],

    "Software - Infrastructure": [
        "MSFT","ORCL","PANW","CRWD",
        "ZS","NET","OKTA","FTNT",
        "MDB","ESTC"
    ],

    "Internet Retail": [
        "AMZN","MELI","PDD","BABA",
        "JD","EBAY","ETSY","SHOP",
        "CPNG","SE"
    ],

    "Electronic Components": [
        "APH","TEL","GLW","JBL",
        "SANM","BHE","CLS","PLXS",
        "VSH","LITE"
    ],

    "Semiconductor Equipment & Materials": [
        "ASML","AMAT","LRCX","KLAC",
        "TER","ENTG","MKSI","ONTO",
        "ACLS","UCTT"
    ],

    "Communication Equipment": [
        "CSCO","ANET","CIEN","JNPR",
        "UI","CALX","COMM","EXTR",
        "INFN","DGII"
    ],

    "Auto Manufacturers": [
        "TSLA","GM","F","RIVN",
        "LCID","NIO","XPEV","LI",
        "TM","HMC"
    ],

    "Banks - Diversified": [
        "JPM","BAC","C","WFC",
        "GS","MS","USB","PNC",
        "TFC","COF"
    ],

    "Capital Markets": [
        "SCHW","BLK","KKR","BX",
        "APO","CME","ICE","NDAQ",
        "SPGI","MCO"
    ],

    "Insurance - Diversified": [
        "BRK-B","AIG","ALL","PGR",
        "TRV","CB","MET","PRU",
        "AFL","HIG"
    ],

    "Oil & Gas Integrated": [
        "XOM","CVX","SHEL","BP",
        "TTE","COP","EOG","OXY",
        "MPC","PSX"
    ],

    "REIT - Industrial": [
        "PLD","REXR","EGP","FR",
        "STAG","TRNO","PLYM","ILPT",
        "LXP","DEA"
    ],

    "Medical Devices": [
        "ABT","SYK","ISRG","BSX",
        "MDT","EW","DXCM","ZBH",
        "HOLX","BAX"
    ],
    "Consumer Electronics": [
    "AAPL",
    "SONY",
    "DELL",
    "HPQ",
    "LOGI",
    "VZIO",
    "GRMN",
    "HIMX",
    "XIAOMI",
    "005930.KS"
    ],
}
st.set_page_config(
    page_title="Exceed Pro",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Exceed Pro")
st.markdown("Historical Probability Analyzer")

# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.header("Settings")

ticker = st.sidebar.text_input(
    "Ticker",
    value="AAPL"
).upper()

years = st.sidebar.slider(
    "Years of History",
    1,
    10,
    5
)

threshold = st.sidebar.number_input(
    "Threshold (%)",
    value=1.0,
    step=0.1
)

recent_window = st.sidebar.selectbox(
    "Recent Window",
    [
        "Full History",
        "Last 20 Days",
        "Last 30 Days",
        "Last 60 Days",
        "Last 90 Days",
        "Last 180 Days"
    ]
)

st.sidebar.header("Filters")

use_rsi = st.sidebar.checkbox("Use RSI Filter")

if use_rsi:
    rsi_option = st.sidebar.selectbox(
        "RSI Condition",
        [
            "RSI <30",
            "RSI 30-70",
            "RSI >70"
        ]
    )

use_volume = st.sidebar.checkbox("Use Volume Filter")

if use_volume:
    volume_option = st.sidebar.selectbox(
        "Volume",
        [
            "Above Average",
            ">2x Average"
        ]
    )

use_ma = st.sidebar.checkbox("Use MA Filter")

if use_ma:
    ma_option = st.sidebar.selectbox(
        "Trend",
        [
            "Above 50 MA",
            "Below 50 MA"
        ]
    )

# -----------------------------
# Download Data
# -----------------------------

@st.cache_data
def load_data(ticker, years):

    

    df = yf.download(
        ticker,
        period=f"{years}y",
        progress=False,
        auto_adjust=True
    )

    return df

df = load_data(ticker, years)

df = load_data(ticker, years)

# Fix MultiIndex columns from yfinance
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# Make sure every column is a Series
for col in ["Open", "High", "Low", "Close", "Volume"]:
    if isinstance(df[col], pd.DataFrame):
        df[col] = df[col].iloc[:, 0]

if df.empty:
    st.error("No data found.")
    st.stop()

# -----------------------------
# Indicators
# -----------------------------

# Previous Close
df["Prev Close"] = df["Close"].shift(1)

# Gap %
df["Gap %"] = (
    (df["Open"] - df["Prev Close"])
    / df["Prev Close"]
) * 100

# High %
df["High %"] = (
    (df["High"] - df["Prev Close"])
    / df["Prev Close"]
) * 100

# Low %
df["Low %"] = (
    (df["Low"] - df["Prev Close"])
    / df["Prev Close"]
) * 100

# Return %
df["Return %"] = (
    (df["Close"] - df["Prev Close"])
    / df["Prev Close"]
) * 100

# 20 MA
df["MA20"] = (
    df["Close"]
    .rolling(20)
    .mean()
)

# 50 MA
df["MA50"] = (
    df["Close"]
    .rolling(50)
    .mean()
)

# Average Volume
df["Avg Volume"] = (
    df["Volume"]
    .rolling(20)
    .mean()
)

# Volume Ratio
df["Volume Ratio"] = (
    df["Volume"]
    / df["Avg Volume"]
)

# -----------------------------
# RSI
# -----------------------------

delta = df["Close"].diff()

gain = delta.clip(lower=0)

loss = -delta.clip(upper=0)

avg_gain = gain.rolling(14).mean()

avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss

df["RSI"] = 100 - (100 / (1 + rs))

# -----------------------------
# Remove NaN rows
# -----------------------------

df = df.dropna()

# -----------------------------
# Apply Recent Window
# -----------------------------

if recent_window == "Last 20 Days":
    df = df.tail(20)

elif recent_window == "Last 30 Days":
    df = df.tail(30)

elif recent_window == "Last 60 Days":
    df = df.tail(60)

elif recent_window == "Last 90 Days":
    df = df.tail(90)

elif recent_window == "Last 180 Days":
    df = df.tail(180)

# -----------------------------
# Apply Filters
# -----------------------------

filtered = df.copy()

if use_rsi:

    if rsi_option == "RSI <30":
        filtered = filtered[filtered["RSI"] < 30]

    elif rsi_option == "RSI 30-70":
        filtered = filtered[
            (filtered["RSI"] >= 30)
            &
            (filtered["RSI"] <= 70)
        ]

    elif rsi_option == "RSI >70":
        filtered = filtered[filtered["RSI"] > 70]

if use_volume:

    if volume_option == "Above Average":
        filtered = filtered[
            filtered["Volume Ratio"] > 1
        ]

    elif volume_option == ">2x Average":
        filtered = filtered[
            filtered["Volume Ratio"] > 2
        ]

if use_ma:

    if ma_option == "Above 50 MA":
        filtered = filtered[
            filtered["Close"] > filtered["MA50"]
        ]

    elif ma_option == "Below 50 MA":
        filtered = filtered[
            filtered["Close"] < filtered["MA50"]
        ]

st.success(f"{len(filtered)} matching historical days found.")

st.subheader("Filtered Data")

st.dataframe(
    filtered.tail(20),
    use_container_width=True
)

# =====================================================
# EXCEED STATISTICS ENGINE
# =====================================================

st.divider()
st.header("📊 Exceed Statistics")

if len(filtered) == 0:
    st.warning("No historical days match the selected filters.")
    st.stop()

# -----------------------------
# Exceed Calculations
# -----------------------------

total_days = len(filtered)

# Days where the intraday high exceeded the target
hit_days = filtered["High %"] >= threshold

hit_count = hit_days.sum()

hit_rate = (hit_count / total_days) * 100

# Basic statistics
avg_high = filtered["High %"].mean()
avg_low = filtered["Low %"].mean()
avg_return = filtered["Return %"].mean()

median_high = filtered["High %"].median()
median_low = filtered["Low %"].median()
median_return = filtered["Return %"].median()

best_day = filtered["High %"].max()
worst_day = filtered["Low %"].min()

std_high = filtered["High %"].std()
std_return = filtered["Return %"].std()

# -----------------------------
# Winning vs Losing Days
# -----------------------------

green_days = (filtered["Return %"] > 0).sum()
red_days = (filtered["Return %"] < 0).sum()

green_pct = (green_days / total_days) * 100
red_pct = (red_days / total_days) * 100

# -----------------------------
# Average Gain on Hit Days
# -----------------------------

if hit_count > 0:
    avg_hit_high = filtered.loc[hit_days, "High %"].mean()
    avg_hit_return = filtered.loc[hit_days, "Return %"].mean()
else:
    avg_hit_high = np.nan
    avg_hit_return = np.nan

# -----------------------------
# Statistics Dashboard
# -----------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Matching Days",
        f"{total_days:,}"
    )

    st.metric(
        "Hit Rate",
        f"{hit_rate:.2f}%"
    )

    st.metric(
        "Hit Days",
        hit_count
    )

with col2:
    st.metric(
        "Average High",
        f"{avg_high:.2f}%"
    )

    st.metric(
        "Average Low",
        f"{avg_low:.2f}%"
    )

    st.metric(
        "Average Return",
        f"{avg_return:.2f}%"
    )

with col3:
    st.metric(
        "Best Day",
        f"{best_day:.2f}%"
    )

    st.metric(
        "Worst Day",
        f"{worst_day:.2f}%"
    )

    st.metric(
        "Std Dev",
        f"{std_return:.2f}"
    )

# -----------------------------
# Detailed Statistics Table
# -----------------------------

stats = pd.DataFrame({
    "Metric": [
        "Matching Days",
        "Hit Days",
        "Hit Rate",
        "Average High",
        "Median High",
        "Average Low",
        "Median Low",
        "Average Return",
        "Median Return",
        "Average High (Hit Days)",
        "Average Return (Hit Days)",
        "Green Days",
        "Red Days",
        "Green %",
        "Red %",
        "Best Day",
        "Worst Day",
        "High Std Dev",
        "Return Std Dev"
    ],
    "Value": [
        total_days,
        hit_count,
        f"{hit_rate:.2f}%",
        f"{avg_high:.2f}%",
        f"{median_high:.2f}%",
        f"{avg_low:.2f}%",
        f"{median_low:.2f}%",
        f"{avg_return:.2f}%",
        f"{median_return:.2f}%",
        f"{avg_hit_high:.2f}%",
        f"{avg_hit_return:.2f}%",
        green_days,
        red_days,
        f"{green_pct:.2f}%",
        f"{red_pct:.2f}%",
        f"{best_day:.2f}%",
        f"{worst_day:.2f}%",
        f"{std_high:.2f}",
        f"{std_return:.2f}"
    ]
})

st.subheader("Detailed Statistics")

st.dataframe(
    stats,
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# Hit Day Distribution
# -----------------------------

st.subheader("Hit vs Miss")

hits = hit_count
misses = total_days - hit_count

fig, ax = plt.subplots(figsize=(5,5))

ax.pie(
    [hits, misses],
    labels=["Hit", "Miss"],
    autopct="%1.1f%%",
    startangle=90
)

ax.set_title("Exceed Probability")

st.pyplot(fig)

# =====================================================
# PREVIOUS CLOSE RECOVERY
# =====================================================

st.divider()
st.header("🔄 Previous Close Recovery")

# -----------------------------
# Recovery Flag
# -----------------------------

# A recovery occurs when the day's HIGH reaches or exceeds
# yesterday's closing price.

filtered["Recovered"] = (
    filtered["High"] >= filtered["Prev Close"]
)

# -----------------------------
# Overall Recovery
# -----------------------------

recovery_days = filtered["Recovered"].sum()

recovery_rate = (
    recovery_days / len(filtered)
) * 100

# -----------------------------
# Recent Window Recovery
# -----------------------------

window_map = {
    "Full History": len(filtered),
    "Last 20 Days": 20,
    "Last 30 Days": 30,
    "Last 60 Days": 60,
    "Last 90 Days": 90,
    "Last 180 Days": 180
}

recent_n = min(
    window_map[recent_window],
    len(filtered)
)

recent = filtered.tail(recent_n)

recent_recovery = recent["Recovered"].sum()

recent_rate = (
    recent_recovery / len(recent)
) * 100

# -----------------------------
# Metrics
# -----------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Overall Recovery %",
        f"{recovery_rate:.2f}%"
    )

with col2:
    st.metric(
        f"{recent_window}",
        f"{recent_rate:.2f}%"
    )

with col3:
    st.metric(
        "Recovered Days",
        f"{recovery_days:,}"
    )

# -----------------------------
# Table
# -----------------------------

windows = [
    20,
    30,
    60,
    90,
    180
]

rows = []

for w in windows:

    temp = filtered.tail(
        min(w, len(filtered))
    )

    hits = temp["Recovered"].sum()

    pct = hits / len(temp) * 100

    rows.append([
        w,
        hits,
        len(temp),
        round(pct,2)
    ])

recovery_table = pd.DataFrame(
    rows,
    columns=[
        "Window",
        "Recovered",
        "Total Days",
        "Recovery %"
    ]
)

st.subheader("Recovery History")

st.dataframe(
    recovery_table,
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# Rolling Recovery Chart
# -----------------------------

rolling = (
    filtered["Recovered"]
    .rolling(20)
    .mean()
    *100
)

fig, ax = plt.subplots(figsize=(12,4))

ax.plot(
    filtered.index,
    rolling,
    linewidth=2
)

ax.set_title(
    "20-Day Rolling Previous Close Recovery %"
)

ax.set_ylabel("%")

ax.grid(True)

st.pyplot(fig)

# -----------------------------
# Recovery by Gap
# -----------------------------

bins = [-100,-4,-3,-2,-1,0,100]

labels = [
    "<-4%",
    "-4% to -3%",
    "-3% to -2%",
    "-2% to -1%",
    "-1% to 0%",
    ">0%"
]

gap_df = filtered.copy()

gap_df["Gap Bucket"] = pd.cut(
    gap_df["Gap %"],
    bins=bins,
    labels=labels
)

gap_stats = (
    gap_df
    .groupby("Gap Bucket")
    ["Recovered"]
    .mean()
    *100
)

st.subheader("Recovery by Opening Gap")

st.bar_chart(gap_stats)

# =====================================================
# CONDITIONAL PROBABILITY ENGINE
# =====================================================

st.divider()
st.header("🎯 Conditional Probability Engine")

# Today's values
today = df.iloc[-1]

today_rsi = today["RSI"]
today_gap = today["Gap %"]
today_vol = today["Volume Ratio"]
today_ma50 = today["MA50"]
today_close = today["Close"]

st.subheader("Today's Conditions")

col1, col2, col3, col4 = st.columns(4)

col1.metric("RSI", f"{today_rsi:.1f}")
col2.metric("Gap %", f"{today_gap:.2f}%")
col3.metric("Volume Ratio", f"{today_vol:.2f}x")
col4.metric("Trend",
            "Above 50 MA" if today_close > today_ma50 else "Below 50 MA")

# ---------------------------------------------------
# Find Similar Historical Days
# ---------------------------------------------------

similar = df.copy()

# Similar RSI (+/-5)
similar = similar[
    (similar["RSI"] >= today_rsi - 5) &
    (similar["RSI"] <= today_rsi + 5)
]

# Similar Gap (+/-0.5%)
similar = similar[
    (similar["Gap %"] >= today_gap - 0.5) &
    (similar["Gap %"] <= today_gap + 0.5)
]

# Similar Volume (+/-25%)
similar = similar[
    (similar["Volume Ratio"] >= today_vol * 0.75) &
    (similar["Volume Ratio"] <= today_vol * 1.25)
]

# Same trend
if today_close > today_ma50:
    similar = similar[
        similar["Close"] > similar["MA50"]
    ]
else:
    similar = similar[
        similar["Close"] < similar["MA50"]
    ]

# Remove today's row
similar = similar.iloc[:-1]

st.write(f"Historical days with similar conditions: **{len(similar)}**")

if len(similar) > 10:

    # Exceed probability
    exceed = (similar["High %"] >= threshold)

    exceed_pct = exceed.mean() * 100

    # Previous close recovery
    recovery = (similar["High"] >= similar["Prev Close"])

    recovery_pct = recovery.mean() * 100

    avg_high = similar["High %"].mean()
    avg_low = similar["Low %"].mean()
    avg_return = similar["Return %"].mean()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Exceed Probability",
        f"{exceed_pct:.2f}%"
    )

    c2.metric(
        "Recovery Probability",
        f"{recovery_pct:.2f}%"
    )

    c3.metric(
        "Matching Days",
        len(similar)
    )

    stats = pd.DataFrame({
        "Statistic":[
            "Average High %",
            "Average Low %",
            "Average Return %"
        ],
        "Value":[
            round(avg_high,2),
            round(avg_low,2),
            round(avg_return,2)
        ]
    })

    st.subheader("Conditional Statistics")

    st.dataframe(
        stats,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Similar Historical Days")

    st.dataframe(
        similar[[
            "Open",
            "High",
            "Low",
            "Close",
            "Gap %",
            "RSI",
            "Volume Ratio",
            "High %",
            "Return %"
        ]].tail(20),
        use_container_width=True
    )

else:

    st.warning(
        "Not enough similar historical days were found. Try increasing the tolerance ranges."
    )

# =====================================================
# SECTOR ANALYSIS
# =====================================================

st.divider()

st.header("🏭 Sector")

sector_df = pd.DataFrame()

try:

    info = yf.Ticker(ticker).info

    industry = info.get("industry", "Unknown")

    st.write("Industry from Yahoo:", industry)

    st.write(industry)

    st.write(f"**Industry:** {industry}")

    peers = industry_peers.get(industry, [])

    if len(peers) == 0:

        st.warning("Industry is not yet supported.")

    else:

        rows = []

        for peer in peers:

            try:

                tk = yf.Ticker(peer)

                hist = tk.history(period="2d")

                if len(hist) < 2:
                    continue

                prev_close = hist["Close"].iloc[-2]

                hist_today = tk.history(
                    period="1d",
                    interval="1m",
                    prepost=True
                    )

                if hist_today.empty:
                        latest = prev_close
                else:
                    latest = hist_today["Close"].iloc[-1]

                market_cap = tk.info.get("marketCap", 0)

                change = (
                    (latest - prev_close)
                    / prev_close
                ) * 100

                rows.append({

                    "Ticker": peer,

                    "Market Cap": market_cap,

                    "Previous Close": prev_close,

                    "Extended Price": latest,

                    "Change %": change

                })

            except:

                pass

        sector_df = pd.DataFrame(rows)

        sector_df = sector_df.sort_values(
            "Market Cap",
            ascending=False
        )

        sector_df = sector_df.head(10)

except Exception as e:
    st.error(f"Sector Error: {e}")
        

# =====================================================
# DISPLAY SECTOR TABLE
# =====================================================

if len(sector_df) > 0:

    sector_df["Market Cap"] = (
        sector_df["Market Cap"] / 1_000_000_000
    ).round(1)

    sector_df["Previous Close"] = sector_df["Previous Close"].round(2)
    sector_df["Extended Price"] = sector_df["Extended Price"].round(2)
    sector_df["Change %"] = sector_df["Change %"].round(2)

    st.dataframe(
        sector_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    sector_avg = sector_df["Change %"].mean()

    sector_median = sector_df["Change %"].median()

    red = (sector_df["Change %"] < 0).sum()

    green = (sector_df["Change %"] >= 0).sum()

    try:
        your_change = float(
            sector_df.loc[
                sector_df["Ticker"] == ticker,
                "Change %"
            ].iloc[0]
        )

        relative = your_change - sector_avg

    except:

        your_change = np.nan
        relative = np.nan

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Sector Average",
        f"{sector_avg:.2f}%"
    )

    c2.metric(
        "Sector Median",
        f"{sector_median:.2f}%"
    )

    c3.metric(
        "Relative Strength",
        f"{relative:.2f}%"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Stocks Green",
        green
    )

    c2.metric(
        "Stocks Red",
        red
    )

    c3.metric(
        "Your Stock",
        f"{your_change:.2f}%"
    )

    st.divider()

    if relative <= -2:

        st.error(
            f"{ticker} is significantly UNDERPERFORMING its sector today."
        )

    elif relative >= 2:

        st.success(
            f"{ticker} is significantly OUTPERFORMING its sector today."
        )

    else:

        st.info(
            f"{ticker} is trading roughly IN LINE with its sector."
        )

else:

    st.warning("No sector data available.")

# =====================================================
# PART 5 - CHARTS & EXPORT
# =====================================================

st.divider()
st.header("📈 Charts")

# -----------------------------
# Price Chart
# -----------------------------

st.subheader(f"{ticker} Price")

fig, ax = plt.subplots(figsize=(12,5))

ax.plot(df.index, df["Close"], linewidth=2)

ax.plot(df.index, df["MA20"], label="MA20")
ax.plot(df.index, df["MA50"], label="MA50")

ax.set_ylabel("Price")
ax.grid(True)
ax.legend()

st.pyplot(fig)

# -----------------------------
# Histogram
# -----------------------------

st.subheader("Distribution of Intraday High %")

fig, ax = plt.subplots(figsize=(10,4))

ax.hist(
    filtered["High %"],
    bins=30
)

ax.axvline(
    threshold,
    linestyle="--",
    linewidth=2,
    label="Threshold"
)

ax.legend()
ax.grid(True)

st.pyplot(fig)

# -----------------------------
# Scatter Plot
# -----------------------------

st.subheader("RSI vs Intraday High")

fig, ax = plt.subplots(figsize=(10,5))

ax.scatter(
    filtered["RSI"],
    filtered["High %"]
)

ax.set_xlabel("RSI")
ax.set_ylabel("High %")
ax.grid(True)

st.pyplot(fig)

# -----------------------------
# Best Historical Days
# -----------------------------

st.subheader("Top 20 Highest Intraday Moves")

top = filtered.sort_values(
    "High %",
    ascending=False
).head(20)

st.dataframe(
    top[
        [
            "Open",
            "High",
            "Low",
            "Close",
            "Gap %",
            "High %",
            "Low %",
            "Return %",
            "RSI",
            "Volume Ratio"
        ]
    ],
    use_container_width=True
)

# -----------------------------
# Download
# -----------------------------

csv = filtered.to_csv().encode("utf-8")

st.download_button(
    "📥 Download Results (CSV)",
    csv,
    file_name=f"{ticker}_exceed_results.csv",
    mime="text/csv"
)

# -----------------------------
# Summary
# -----------------------------

st.divider()

st.header("📋 Summary")

summary = pd.DataFrame({

    "Metric":[
        "Ticker",
        "Threshold",
        "Historical Days",
        "Hit Rate",
        "Recovery Rate",
        "Average High",
        "Average Low",
        "Average Return"
    ],

    "Value":[
        ticker,
        f"{threshold:.2f}%",
        len(filtered),
        f"{hit_rate:.2f}%",
        f"{recovery_rate:.2f}%",
        f"{avg_high:.2f}%",
        f"{avg_low:.2f}%",
        f"{avg_return:.2f}%"
    ]

})

st.dataframe(
    summary,
    hide_index=True,
    use_container_width=True
)

st.success("✅ Exceed Pro Analysis Complete")
