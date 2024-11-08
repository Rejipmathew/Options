import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Streamlit App Title
st.title("📈 Stock Price Dashboard")

# Sidebar for user input
st.sidebar.header("User Input")

# Get stock ticker symbol from user
ticker = st.sidebar.text_input("Enter Stock Ticker Symbol (e.g., AAPL, TSLA, MSFT)", "AAPL")

# Date range selection
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))

# Load stock data using yfinance
@st.cache_data
def load_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    data.reset_index(inplace=True)
    return data

data = load_data(ticker, start_date, end_date)

# Display Data
if not data.empty:
    st.subheader(f"Stock Data for {ticker.upper()}")
    st.write(data.tail())
    
    # Line plot of stock closing price
    st.subheader("Closing Price")
    st.line_chart(data['Close'])

    # Plot Moving Averages
    st.subheader("Moving Averages")
    ma_short = st.sidebar.slider("Short Moving Average (days)", 5, 50, 20)
    ma_long = st.sidebar.slider("Long Moving Average (days)", 50, 200, 100)
    data[f'SMA_{ma_short}'] = data['Close'].rolling(window=ma_short).mean()
    data[f'SMA_{ma_long}'] = data['Close'].rolling(window=ma_long).mean()
    
    plt.figure(figsize=(10, 6))
    plt.plot(data['Date'], data['Close'], label="Close Price", alpha=0.5)
    plt.plot(data['Date'], data[f'SMA_{ma_short}'], label=f"SMA {ma_short}", alpha=0.75)
    plt.plot(data['Date'], data[f'SMA_{ma_long}'], label=f"SMA {ma_long}", alpha=0.75)
    plt.legend()
    st.pyplot(plt)

    # Volume
    st.subheader("Volume")
    st.bar_chart(data['Volume'])
else:
    st.error("No data found for the given ticker and date range.")

# Add footer
st.write("Data Source: Yahoo Finance")
