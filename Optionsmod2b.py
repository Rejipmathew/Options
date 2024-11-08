import streamlit as st
import yfinance as yf
import pandas as pd

# Streamlit app title
st.title("Stock Analysis Dashboard")

# User input for stock ticker
ticker_input = st.text_input("Enter stock ticker (e.g., MSFT):", value="MSFT")
ticker = yf.Ticker(ticker_input)

# Sidebar for navigation
st.sidebar.header("Choose Data to Display")
options = st.sidebar.multiselect(
    "Select the data you want to explore:",
    ["Stock Info", "Historical Data", "Dividends", "Actions", "Financials", 
     "Holders", "Recommendations", "Analysts Data", "Earnings Dates", "Options Data", "News"],
    default=["Stock Info", "Historical Data"]
)

# Display stock information
if "Stock Info" in options:
    st.subheader(f"Stock Information: {ticker_input}")
    try:
        stock_info = ticker.info
        st.write(f"**Company Name**: {stock_info.get('longName', 'N/A')}")
        st.write(f"**Sector**: {stock_info.get('sector', 'N/A')}")
        st.write(f"**Industry**: {stock_info.get('industry', 'N/A')}")
        st.write(f"**Market Cap**: {stock_info.get('marketCap', 'N/A')}")
        st.write(f"**52-Week High**: {stock_info.get('fiftyTwoWeekHigh', 'N/A')}")
        st.write(f"**52-Week Low**: {stock_info.get('fiftyTwoWeekLow', 'N/A')}")
    except Exception as e:
        st.error(f"Could not retrieve stock information: {e}")

# Display historical data with visualization
if "Historical Data" in options:
    st.subheader("Historical Market Data")
    period = st.selectbox("Select the period:", ["1mo", "3mo", "6mo", "1y", "5y", "max"], index=0)
    interval = st.selectbox("Select the interval:", ["1d", "1wk", "1mo"], index=0)
    hist = ticker.history(period=period, interval=interval)
    
    if not hist.empty:
        st.line_chart(hist['Close'], height=300)
        st.write(hist)
    else:
        st.warning("No historical data available.")

# Display dividends and actions
if "Dividends" in options:
    st.subheader("Dividends")
    st.line_chart(ticker.dividends)
    st.write(ticker.dividends)

if "Actions" in options:
    st.subheader("Stock Actions")
    st.write(ticker.actions)

# Display financials (income statement, balance sheet, cash flow)
if "Financials" in options:
    st.subheader("Financial Statements")
    st.write("**Quarterly Income Statement**")
    st.write(ticker.quarterly_income_stmt)

    st.write("**Quarterly Balance Sheet**")
    st.write(ticker.quarterly_balance_sheet)

    st.write("**Quarterly Cash Flow**")
    st.write(ticker.quarterly_cashflow)

# Display holders
if "Holders" in options:
    st.subheader("Holders")
    st.write("**Major Holders**")
    st.write(ticker.major_holders)

    st.write("**Institutional Holders**")
    st.write(ticker.institutional_holders)

    st.write("**Mutual Fund Holders**")
    st.write(ticker.mutualfund_holders)

# Display recommendations and analyst data
if "Recommendations" in options:
    st.subheader("Recommendations")
    st.write(ticker.recommendations)
    st.write("**Upgrades and Downgrades**")
    st.write(ticker.upgrades_downgrades)

if "Analysts Data" in options:
    st.subheader("Analyst Estimates")
    st.write("**Analyst Price Targets**")
    st.write(ticker.analyst_price_targets)

    st.write("**Earnings Estimates**")
    st.write(ticker.earnings_estimate)

    st.write("**Revenue Estimates**")
    st.write(ticker.revenue_estimate)

    st.write("**EPS Trend**")
    st.write(ticker.eps_trend)

    st.write("**Growth Estimates**")
    st.write(ticker.growth_estimates)

# Display earnings dates
if "Earnings Dates" in options:
    st.subheader("Earnings Dates")
    st.write(ticker.earnings_dates)

# Display options data
if "Options Data" in options:
    st.subheader("Options Data")
    expirations = ticker.options
    if expirations:
        selected_expiry = st.selectbox("Select expiration date:", expirations)
        opt_chain = ticker.option_chain(selected_expiry)
        st.write("**Calls**")
        st.write(opt_chain.calls)
        st.write("**Puts**")
        st.write(opt_chain.puts)
    else:
        st.warning("No options data available.")

# Display news
if "News" in options:
    st.subheader("Latest News")
    news = ticker.news
    if news:
        for article in news:
            st.write(f"**{article['title']}**")
            st.write(f"{article['publisher']} - {article['providerPublishTime']}")
            st.write(f"[Read more]({article['link']})")
    else:
        st.warning("No news articles available.")

