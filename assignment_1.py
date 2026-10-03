import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from stock import Stock

st.set_page_config(page_title="Stock Analysis App", layout="wide")

# Cached data wrapper function to instantiate Stock objects safely
@st.cache_data
def load_stock_data(symbol, start, end, ma_short, ma_long):
    # Instantiate stock with short moving average window
    stock = Stock(symbol=symbol, start=start, end=end, ma_window=ma_short)
    
    # Dynamically compute long moving average directly on stock.data if retrieval succeeded
    if stock.data is not None and not stock.data.empty:
        stock.data['MA_long'] = stock.data['Close'].rolling(window=ma_long).mean()
        
    return stock


st.title("Stock Analysis & Portfolio Comparison")

# Sidebar inputs shared across tabs
st.sidebar.header("Controls")
default_symbol = st.sidebar.text_input("Ticker Symbol (Tab 1)", value="AAPL")

default_start = datetime.today() - timedelta(days=365)
default_end = datetime.today()

start_date = st.sidebar.date_input("Start Date", value=default_start)
end_date = st.sidebar.date_input("End Date", value=default_end)

st.sidebar.subheader("Moving Averages")
ma_short_win = st.sidebar.slider("Short MA Window", min_value=5, max_value=200, value=10)
ma_long_win = st.sidebar.slider("Long MA Window", min_value=5, max_value=200, value=50)

# Create App Tabs
tab1, tab2 = st.tabs(["Single Stock Analysis", "Portfolio Comparison"])

# ==========================================
# TAB 1: Single Stock Analysis
# ==========================================
with tab1:
    st.header(f"Single Stock Analysis: {default_symbol.upper()}")
    
    if st.button("Fetch Stock Data", key="fetch_single"):
        with st.spinner(f"Fetching data for {default_symbol}..."):
            stock = load_stock_data(
                symbol=default_symbol.strip().upper(),
                start=start_date,
                end=end_date,
                ma_short=ma_short_win,
                ma_long=ma_long_win
            )
            
        if stock.data is None or stock.data.empty:
            st.error(stock.message)
        else:
            st.success(stock.message)
            
            # Metrics Display
            last_close = stock.data['Close'].iloc[-1]
            cum_return = stock.data['return'].sum()
            trading_days = len(stock.data)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Last Close Price", f"${last_close:.2f}")
            col2.metric("Cumulative Return", f"{cum_return * 100:.2f}%")
            col3.metric("Trading Days", f"{trading_days}")
            
            st.markdown("---")
            
            # Plotly Price Chart with Dual Moving Averages built from stock.data
            st.subheader("Price History & Moving Averages")
            fig_price = go.Figure()
            
            fig_price.add_trace(go.Scatter(
                x=stock.data.index, y=stock.data['Close'],
                mode='lines', name='Close Price', line=dict(color='#1f77b4')
            ))
            
            fig_price.add_trace(go.Scatter(
                x=stock.data.index, y=stock.data['MA'],
                mode='lines', name=f'MA Short ({ma_short_win}d)', line=dict(color='#ff7f0e')
            ))
            
            fig_price.add_trace(go.Scatter(
                x=stock.data.index, y=stock.data['MA_long'],
                mode='lines', name=f'MA Long ({ma_long_win}d)', line=dict(color='#9467bd')
            ))
            
            fig_price.update_layout(
                title=f"{stock.symbol} Price & Moving Averages",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                hovermode="x unified"
            )
            st.plotly_chart(fig_price, use_container_width=True)
            
            # Stock class figures
            col_left, col_right = st.columns(2)
            with col_left:
                st.subheader("Cumulative Performance")
                fig_perf = stock.plot_performance()
                st.plotly_chart(fig_perf, use_container_width=True)
                
            with col_right:
                st.subheader("Daily Returns Distribution")
                fig_dist = stock.plot_return_dist()
                st.plotly_chart(fig_dist, use_container_width=True)
                
            # Returns Summary Table
            st.subheader("Daily Return Statistics")
            stats_df = stock.data['return'].describe().to_frame().T
            st.dataframe(stats_df, use_container_width=True)


# ==========================================
# TAB 2: Portfolio Comparison
# ==========================================
with tab2:
    st.header("Portfolio Comparison")
    
    portfolio_input = st.text_input(
        "Enter Ticker Symbols (comma-separated):", 
        value="AAPL, MSFT, GOOG"
    )
    
    if st.button("Compare Portfolio", key="fetch_portfolio"):
        tickers = [t.strip().upper() for t in portfolio_input.split(",") if t.strip()]
        
        if not tickers:
            st.warning("Please enter at least one valid ticker symbol.")
        else:
            cum_returns_df = pd.DataFrame()
            
            with st.spinner("Downloading portfolio data..."):
                for ticker in tickers:
                    stock_obj = load_stock_data(
                        symbol=ticker,
                        start=start_date,
                        end=end_date,
                        ma_short=ma_short_win,
                        ma_long=ma_long_win
                    )
                    
                    if stock_obj.data is None or stock_obj.data.empty:
                        st.error(f"Error for {ticker}: {stock_obj.message}")
                    else:
                        # Zero-based cumulative return calculation: cumsum starting explicitly at 0.0
                        series_cum = stock_obj.data['return'].cumsum()
                        series_cum = series_cum - series_cum.iloc[0]
                        cum_returns_df[ticker] = series_cum
            
            if not cum_returns_df.empty:
                st.subheader("Zero-Based Cumulative Performance Comparison")
                
                fig_port = px.line(
                    cum_returns_df,
                    x=cum_returns_df.index,
                    y=cum_returns_df.columns,
                    title="Comparative Cumulative Returns (Zero-Based)",
                    labels={"value": "Cumulative Return", "index": "Date", "variable": "Ticker"}
                )
                
                fig_port.add_hline(y=0, line_dash='dash', line_color='black', opacity=0.7)
                fig_port.update_layout(yaxis_tickformat='.1%', hovermode='x unified')
                
                st.plotly_chart(fig_port, use_container_width=True)