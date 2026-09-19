from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

END = date.today()
START = date.today() - timedelta(days=365)

st.set_page_config(layout="wide", page_title="Stock Price Analysis", page_icon="📈")
("Stock Price Analysis")
st.title("Stock Analysis")

st.sidebar.title("Input")
ticker = st.sidebar.text_input ("Error stock ticker symbol", value="AAPL")
comparison_ticker = st.sidebar.text_input ("Comparison ticker symbol", value="SPY")
col1, col2 = st.sidebar.columns(2)
tab1, tab2, tab3 = st.tabs(["Stock 1", "Stock 2", "Comparison"])
start_date = st.sidebar.date_input( "Start Date", START)
end_date = st.sidebar.date_input( "End Date", END)

mv_avg = st.sidebar.slider("Moving Average",
                           min_value = 0,
                           max_value = 100,
                           value = 50,
                           step = 1)
run_analysis = st.sidebar.button("Run Analysis")

def get_stock_data(ticker, start_date, end_date):

    try:
        data = yf.download(ticker, start_date, end_date)
        if data.empty:
            return None, f"No data for {ticker}"
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data, f"Successfully downloaded data for {ticker}"
    except Exception as e:
        return None, f"Download failed due to {e}"


if run_analysis:
    get_stock_data(ticker, start_date, end_date)
    if get_stock_data(ticker, start_date, end_date) is None:
        st.error("Stock data not available")
        st.stop()
    if comparison_ticker is None:
        st.error("Comparison ticker not available")
        st.stop()
    df["normalized_close"] = (df["Close"] / df["Close"].iloc[0]) * 100
    comparison_df["normalized_close"] = (comparison_df["Close"] / comparison_df["Close"].iloc[0]) * 100

with tab3:
    fig = px.line(title=f"{ticker} vs {comparison_ticker} Performance (Base 100)")
    fig.add_scatter(x=df.index, y=df["normalized_close"], name=ticker)
    fig.add_scatter(x=comparison_df.index, y=comparison_df["normalized_close"], name=comparison_ticker)
    st.plotly_chart(fig)

    summary = pd.DataFrame({
        "Ticker": [ticker, comparison_ticker],
        "Min": [df["normalized_close"].min(), comparison_df["normalized_close"].min()],
        "Max": [df["normalized_close"].max(), comparison_df["normalized_close"].max()],
        "Final": [df["normalized_close"].iloc[-1], comparison_df["normalized_close"].iloc[-1]],
    })
    st.dataframe(summary)
