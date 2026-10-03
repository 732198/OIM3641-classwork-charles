from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

END = date.today()
START = date.today() - timedelta(days=365)

st.set_page_config(layout="wide", page_title="Stock Price Analysis", page_icon="📈")
st.title("Stock Analysis (Modified Demo)")

st.sidebar.title("Input")
ticker = st.sidebar.text_input("Stock Ticker Symbol", value="AAPL")

start_date = st.sidebar.date_input("Start Date", START)
end_date = st.sidebar.date_input("End Date", END)

# Dual moving average sliders added directly to demo
ma_short = st.sidebar.slider("Short Moving Average Window", min_value=5, max_value=200, value=10, step=1)
ma_long = st.sidebar.slider("Long Moving Average Window", min_value=5, max_value=200, value=50, step=1)

run_analysis = st.sidebar.button("Run Analysis", type="primary")


def get_stock_data(ticker, start_date, end_date):
    try:
        data = yf.download(ticker, start_date, end_date, progress=False)
        if data.empty:
            return None, f"No data for {ticker}"
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data, f"Successfully downloaded data for {ticker}"
    except Exception as e:
        return None, f"Download failed due to {e}"


if run_analysis:
    with st.spinner(f"Fetching {ticker} data..."):
        df, msg = get_stock_data(ticker, start_date, end_date)
        if df is not None:
            st.sidebar.success(msg)
        else:
            st.sidebar.error(msg)
            st.stop()

        # Calculate short and long moving averages
        df['MA_short'] = df['Close'].rolling(window=ma_short).mean()
        df['MA_long'] = df['Close'].rolling(window=ma_long).mean()
        df['pct_chg'] = df.Close.pct_change()

        tab1, tab2, tab3 = st.tabs(["Chart", "Statistics", "Raw Data"])

        with tab1:
            st.subheader(f"{ticker} Price Analysis")
            col1, col2, col3 = st.columns(3)
            col1.metric("Last Price", f"{df.Close.iloc[-1]:.2f}")
            col2.metric("Cum. Change", f"{df.Close.iloc[-1]/df.Close.iloc[0]-1:.2%}")
            col3.metric("Trading Days", f"{df.Close.count()}")

            # Plot Close along with both moving averages
            fig = px.line(df, y=["Close", "MA_short", "MA_long"])
            fig.update_layout(hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.subheader(f"{ticker} Summary Statistics")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Daily Change Stats**")
                summary = df["pct_chg"].describe()
                st.dataframe(summary)
            with col2:
                st.write("**Price Stats**")
                price_stats = pd.DataFrame({
                    'Metric': ['High', 'Low', 'Mean', 'Volatility'],
                    'Values': [
                        f"{df.Close.max():.2f}",
                        f"{df.Close.min():.2f}",
                        f"{df.Close.mean():.2f}",
                        f"{df.Close.std():.2f}"
                    ]
                })
                st.dataframe(price_stats)

        with tab3:
            st.subheader(f"{ticker} Raw Data")
            csv = df.to_csv()
            st.download_button(
                "Download Raw Data",
                csv,
                file_name=f"{ticker}_Raw_Data.csv",
                mime="text/csv",
            )