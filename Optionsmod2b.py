import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st

# Streamlit app title
st.title("Option Trading Indicators without TA-Lib")

# User input for stock ticker
ticker_input = st.text_input("Enter stock ticker (e.g., AAPL):", value="AAPL")

# Function to fetch stock data with caching
@st.cache_data
def get_ticker_data(ticker_input):
    return yf.Ticker(ticker_input)

# Function to fetch stock information with caching
@st.cache_data
def get_stock_info(ticker):
    return ticker.info

# Function to fetch historical data with caching
@st.cache_data
def get_historical_data(ticker, period, interval):
    return ticker.history(period=period, interval=interval)

# Function to fetch options data with caching
@st.cache_data
def get_option_chain(ticker, expiry):
    return ticker.option_chain(expiry)

# Load stock data using yfinance
ticker = get_ticker_data(ticker_input)

# Display basic stock information
st.subheader(f"Stock Information: {ticker_input}")

try:
    stock_info = get_stock_info(ticker)
    price = stock_info.get('regularMarketPrice', 'N/A')
    market_cap = stock_info.get('marketCap', 'N/A')
    fifty_two_week_high = stock_info.get('fiftyTwoWeekHigh', 'N/A')
    fifty_two_week_low = stock_info.get('fiftyTwoWeekLow', 'N/A')

    st.write(f"Price: {price}")
    st.write(f"Market Cap: {market_cap}")
    st.write(f"52-Week High: {fifty_two_week_high}")
    st.write(f"52-Week Low: {fifty_two_week_low}")

except Exception as e:
    st.write(f"Could not retrieve stock information: {e}")

# Fetch historical data
period = st.selectbox("Choose time period for historical data:", ['1mo', '3mo', '6mo', '1y', '5y'])
interval = st.selectbox("Choose time interval:", ['1d', '1wk', '1mo'])
historical_data = get_historical_data(ticker, period, interval)

# Display a line chart for the stock's closing price
st.subheader("Historical Stock Prices")
st.line_chart(historical_data['Close'])

# Custom RSI calculation
def calculate_rsi(data, window):
    delta = data.diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Custom Bollinger Bands calculation
def calculate_bollinger_bands(data, window, num_std):
    rolling_mean = data.rolling(window).mean()
    rolling_std = data.rolling(window).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return upper_band, rolling_mean, lower_band

# Custom Intraday Momentum Index (IMI) calculation
def calculate_imi(open_data, close_data, window):
    up = (close_data > open_data).astype(int) * (close_data - open_data)
    down = (open_data > close_data).astype(int) * (open_data - close_data)
    imi = 100 * (up.rolling(window).sum() / (up.rolling(window).sum() + down.rolling(window).sum()))
    return imi

# Custom Money Flow Index (MFI) calculation
def calculate_mfi(high, low, close, volume, window):
    typical_price = (high + low + close) / 3
    money_flow = typical_price * volume
    positive_flow = (money_flow.where(close > close.shift(1), 0)).rolling(window).sum()
    negative_flow = (money_flow.where(close < close.shift(1), 0)).rolling(window).sum()
    money_flow_ratio = positive_flow / negative_flow
    mfi = 100 - (100 / (1 + money_flow_ratio))
    return mfi

# Calculate and display RSI
st.subheader("Relative Strength Index (RSI)")
rsi_period = st.slider("Choose RSI period:", min_value=5, max_value=30, value=14)
rsi = calculate_rsi(historical_data['Close'], rsi_period)
st.line_chart(rsi)

# Calculate and display Bollinger Bands
st.subheader("Bollinger Bands")
bb_period = st.slider("Choose Bollinger Bands period:", min_value=10, max_value=50, value=20)
num_std = st.slider("Choose number of standard deviations:", min_value=1, max_value=3, value=2)
upper_band, middle_band, lower_band = calculate_bollinger_bands(historical_data['Close'], bb_period, num_std)
bollinger_df = pd.DataFrame({'Upper Band': upper_band, 'Middle Band': middle_band, 'Lower Band': lower_band})
st.line_chart(bollinger_df)

# Calculate and display IMI
st.subheader("Intraday Momentum Index (IMI)")
imi_period = st.slider("Choose IMI period:", min_value=5, max_value=30, value=14)
imi = calculate_imi(historical_data['Open'], historical_data['Close'], imi_period)
st.line_chart(imi)

# Calculate and display MFI
st.subheader("Money Flow Index (MFI)")
mfi_period = st.slider("Choose MFI period:", min_value=5, max_value=30, value=14)
mfi = calculate_mfi(historical_data['High'], historical_data['Low'], historical_data['Close'], historical_data['Volume'], mfi_period)
st.line_chart(mfi)

# Display available option expiration dates
st.subheader("Available Option Expiration Dates")
expirations = ticker.options
if expirations:
    selected_expiry = st.selectbox("Choose expiration date:", expirations)

    # Load option chain for the selected expiration date
    option_chain = get_option_chain(ticker, selected_expiry)
    calls = option_chain.calls
    puts = option_chain.puts

    calls_sorted = calls[['strike', 'openInterest']].sort_values(by='openInterest', ascending=False)
    puts_sorted = puts[['strike', 'openInterest']].sort_values(by='openInterest', ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Calls Open Interest (Descending)")
        st.write(calls_sorted)

    with col2:
        st.subheader("Puts Open Interest (Descending)")
        st.write(puts_sorted)

    st.subheader("Put-Call Ratio (PCR) Indicator")
    put_call_ratio = puts['openInterest'].sum() / calls['openInterest'].sum()
    st.write(f"Put-Call Ratio: {put_call_ratio:.2f}")
else:
    st.write("No option expiration dates available for this ticker.")
