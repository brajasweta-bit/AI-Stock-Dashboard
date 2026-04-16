import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import timedelta

from data import get_stock_data
from indicators import add_indicators
from predict import predict_signal

st.set_page_config(page_title="AI Trading Terminal", layout="wide")

# ---------------- SIDEBAR ---------------- #

page = st.sidebar.selectbox(
    "Navigation",
    [
        "🏠 Home",
        "📈 AI Stock Analyzer",
        "📊 Top Movers",
        "💼 Portfolio",
        "🌍 Market Overview",
        "📰 News"
    ]
)

# ---------------- HOME ---------------- #

if page == "🏠 Home":

    st.title("🚀 AI Trading Terminal")

    st.write("Advanced AI Powered Stock Analysis Platform")

    col1,col2,col3 = st.columns(3)

    with col1:
        st.info("📈 AI Buy/Sell Prediction")

    with col2:
        st.info("📊 Technical Indicators")

    with col3:
        st.info("🧠 AI Price Forecast")

    st.write("Use the sidebar to explore the dashboard.")

# ---------------- AI ANALYZER ---------------- #

elif page == "📈 AI Stock Analyzer":

    st.title("📊 AI Stock Analyzer")

    stock = st.text_input("Stock Symbol","AAPL")

    period = st.selectbox(
        "Period",
        ["1y","2y","5y"]
    )

    if st.button("Analyze"):

        df = get_stock_data(stock,period)

        if df.empty:
            st.error("Stock not found")
            st.stop()

        df = add_indicators(df)
        df = df.dropna()

        signal,confidence = predict_signal(df)

        col1,col2 = st.columns(2)

        with col1:
            st.metric("AI Signal",signal)

        with col2:
            st.metric("Confidence",f"{round(confidence*100,2)}%")

        # Market Trend

        if float(df["MA50"].iloc[-1]) > float(df["MA200"].iloc[-1]):
            st.success("Market Trend: Bullish 🟢")
        else:
            st.error("Market Trend: Bearish 🔴")

        # Support / Resistance

        support = float(df["Low"].tail(20).min())
        resistance = float(df["High"].tail(20).max())

        # Candlestick

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"]
        ))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["MA50"],
            name="MA50"
        ))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["MA200"],
            name="MA200"
        ))

        fig.add_hline(y=support)
        fig.add_hline(y=resistance)

        st.plotly_chart(fig,use_container_width=True)

        # RSI

        st.subheader("RSI Indicator")

        rsi = go.Figure()

        rsi.add_trace(go.Scatter(
            x=df.index,
            y=df["RSI"]
        ))

        rsi.add_hline(y=70)
        rsi.add_hline(y=30)

        st.plotly_chart(rsi,use_container_width=True)

        # MACD

        st.subheader("MACD Indicator")

        macd = go.Figure()

        macd.add_trace(go.Scatter(
            x=df.index,
            y=df["MACD"],
            name="MACD"
        ))

        macd.add_trace(go.Scatter(
            x=df.index,
            y=df["MACD_signal"],
            name="Signal"
        ))

        st.plotly_chart(macd,use_container_width=True)

        # ---------------- AI FORECAST ---------------- #

        st.subheader("📈 AI Price Forecast (Simple Model)")

        last_price = float(df["Close"].iloc[-1])

        future_prices = []

        for i in range(30):
            change = np.random.normal(0,1)
            last_price = last_price + change
            future_prices.append(last_price)

        future_dates = [
            df.index[-1] + timedelta(days=i)
            for i in range(1,31)
        ]

        forecast = go.Figure()

        forecast.add_trace(go.Scatter(
            x=df.index,
            y=df["Close"],
            name="Historical"
        ))

        forecast.add_trace(go.Scatter(
            x=future_dates,
            y=future_prices,
            name="Forecast"
        ))

        st.plotly_chart(forecast,use_container_width=True)

# ---------------- TOP MOVERS ---------------- #

elif page == "📊 Top Movers":

    st.title("📊 Top Gainers / Losers")

    stocks = [
        "AAPL","TSLA","MSFT","NVDA","META",
        "AMZN","GOOGL","NFLX"
    ]

    results = []

    for s in stocks:

        data = yf.download(s,period="5d")

        if not data.empty:

            price = float(data["Close"].iloc[-1])
            prev = float(data["Close"].iloc[-2])

            change = ((price-prev)/prev)*100

            results.append((s,round(change,2)))

    df = pd.DataFrame(results,columns=["Stock","Change %"])

    gainers = df.sort_values("Change %",ascending=False).head(5)
    losers = df.sort_values("Change %").head(5)

    col1,col2 = st.columns(2)

    with col1:
        st.subheader("🚀 Top Gainers")
        st.table(gainers)

    with col2:
        st.subheader("📉 Top Losers")
        st.table(losers)

# ---------------- PORTFOLIO ---------------- #

elif page == "💼 Portfolio":

    st.title("💼 Portfolio Tracker")

    if "portfolio" not in st.session_state:
        st.session_state.portfolio = []

    stock = st.text_input("Stock")

    qty = st.number_input("Quantity",1)

    price = st.number_input("Buy Price")

    if st.button("Add"):

        st.session_state.portfolio.append({
            "stock":stock,
            "qty":qty,
            "price":price
        })

    total_profit = 0

    for item in st.session_state.portfolio:

        data = yf.download(item["stock"],period="1d")

        if not data.empty:

            current = float(data["Close"].iloc[-1])

            profit = (current-item["price"])*item["qty"]

            total_profit += profit

            st.write(
                f"{item['stock']} | Shares: {item['qty']} | P/L: {round(profit,2)}"
            )

    st.subheader(f"Total Portfolio P/L: {round(total_profit,2)}")

# ---------------- MARKET OVERVIEW ---------------- #

elif page == "🌍 Market Overview":

    st.title("🌍 Market Overview")

    indices = {
        "S&P 500":"^GSPC",
        "NASDAQ":"^IXIC",
        "DOW JONES":"^DJI"
    }

    for name,ticker in indices.items():

        data = yf.download(ticker,period="5d")

        if not data.empty:

            price = float(data["Close"].iloc[-1])
            prev = float(data["Close"].iloc[-2])

            delta = price-prev

            st.metric(name,round(price,2),round(delta,2))

# ---------------- NEWS ---------------- #

elif page == "📰 News":

    st.title("📰 Market News")

    st.write("Latest Market Insights")

    st.write("• AI companies continue strong rally")

    st.write("• Tech sector driving global markets")

    st.write("• Investors watching inflation data")

    st.info("Real-time news API can be added.")