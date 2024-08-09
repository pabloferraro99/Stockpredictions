import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px

def normalize_value(value, min_value, max_value, inverse=False):
    """Normalize the value to a 0-100 scale."""
    normalized = (value - min_value) / (max_value - min_value) * 100
    if inverse:
        return 100 - normalized
    return normalized

def calculate_composite_score(values, weights):
    return np.average(values, weights=weights)

def calculate_moving_averages(stock_data):
    stock_data['MA10'] = stock_data['Close'].rolling(window=10).mean()
    stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()
    stock_data['MA200'] = stock_data['Close'].rolling(window=200).mean()
    return stock_data

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_sharpe_ratio(stock_data):
    daily_returns = stock_data['Close'].pct_change().dropna()
    avg_daily_return = daily_returns.mean()
    std_daily_return = daily_returns.std()
    sharpe_ratio = avg_daily_return / std_daily_return * np.sqrt(252)
    return sharpe_ratio

def show_investment_decision():
    st.title("Investment Decision Index")

    # Input fields for ticker and date range
    ticker = st.text_input("Enter the ticker symbol (e.g., NVDA for NVIDIA):", value="^IXIC")
    start_date = st.date_input("Start date:", value=pd.to_datetime("2019-04-01"))
    end_date = st.date_input("End date:", value=pd.to_datetime('today'))

    # Slider for risk preference
    risk_preference = st.slider("Select your risk preference (1-5):", 1, 5, 3)

    # Fetch data based on inputs
    @st.cache_data
    def fetch_data(ticker, start, end):
        data = yf.download(ticker, start=start, end=end)
        data.reset_index(inplace=True)
        return data

    # Fetch the stock data
    stock_data = fetch_data(ticker, start_date, end_date)

    # Calculate moving averages
    stock_data = calculate_moving_averages(stock_data)

    # Calculate various indicators
    historical_volatility = stock_data['Close'].pct_change().std() * np.sqrt(252) * 100
    monte_carlo_mean_price = stock_data['Close'].mean()
    rsi = calculate_rsi(stock_data)
    sharpe_ratio = calculate_sharpe_ratio(stock_data)

    # Normalize indicators to a 0-100 scale
    normalized_historical_volatility = normalize_value(historical_volatility, 0, 100, inverse=True)  # Inverse because lower is better
    normalized_monte_carlo_mean_price = normalize_value(monte_carlo_mean_price, 0, stock_data['Close'].max())
    normalized_ma10 = normalize_value(stock_data['MA10'].iloc[-1], 0, stock_data['Close'].max())
    normalized_ma50 = normalize_value(stock_data['MA50'].iloc[-1], 0, stock_data['Close'].max())
    normalized_ma200 = normalize_value(stock_data['MA200'].iloc[-1], 0, stock_data['Close'].max())
    normalized_rsi = normalize_value(rsi, 0, 100, inverse=True)  # Inverse normalization for RSI
    normalized_sharpe_ratio = normalize_value(sharpe_ratio, -2, 5)  # Assuming -2 to 5 as reasonable range

    # Create the list of normalized indicator values
    indicators = {
        "historical_volatility": normalized_historical_volatility,
        "monte_carlo_mean_price": normalized_monte_carlo_mean_price,
        "ma10": normalized_ma10,
        "ma50": normalized_ma50,
        "ma200": normalized_ma200,
        "rsi": normalized_rsi,
        "sharpe_ratio": normalized_sharpe_ratio
    }

    # Define weights for each indicator based on risk preference
    if risk_preference == 1:
        weights = {
            "historical_volatility": 0.4,
            "monte_carlo_mean_price": 0.1,
            "ma10": 0.1,
            "ma50": 0.1,
            "ma200": 0.1,
            "rsi": 0.1,
            "sharpe_ratio": 0.1,
        }
    elif risk_preference == 2:
        weights = {
            "historical_volatility": 0.3,
            "monte_carlo_mean_price": 0.1,
            "ma10": 0.1,
            "ma50": 0.1,
            "ma200": 0.1,
            "rsi": 0.1,
            "sharpe_ratio": 0.2,
        }
    elif risk_preference == 3:
        weights = {
            "historical_volatility": 0.2,
            "monte_carlo_mean_price": 0.15,
            "ma10": 0.1,
            "ma50": 0.1,
            "ma200": 0.1,
            "rsi": 0.1,
            "sharpe_ratio": 0.25,
        }
    elif risk_preference == 4:
        weights = {
            "historical_volatility": 0.1,
            "monte_carlo_mean_price": 0.2,
            "ma10": 0.1,
            "ma50": 0.1,
            "ma200": 0.1,
            "rsi": 0.1,
            "sharpe_ratio": 0.3,
        }
    else:  # risk_preference == 5
        weights = {
            "historical_volatility": 0.05,
            "monte_carlo_mean_price": 0.25,
            "ma10": 0.1,
            "ma50": 0.1,
            "ma200": 0.1,
            "rsi": 0.1,
            "sharpe_ratio": 0.3,
        }

    # Calculate composite score
    composite_score = calculate_composite_score(list(indicators.values()), list(weights.values()))

    # Display the results
    st.write(f"Composite Score: {composite_score:.2f}")

    # Display investment outlook based on composite score
    if composite_score > 60:
        st.write("🚀 The investment outlook is positive.")
    elif composite_score > 40:
        st.write("🤔 The investment outlook is neutral.")
    else:
        st.write("⚠️ The investment outlook is negative.")


           
           
           
# Create a bar chart with a pointer for Composite Score
    fig_composite = go.Figure()
    fig_composite.add_trace(go.Bar(
        x=[100],  # Full length of the bar
        y=[''],
        orientation='h',
        marker=dict(
            color='rgba(255, 255, 255, 0)',  # Transparent bar
            line=dict(color='black', width=2)
        )
    ))

    fig_composite.add_shape(
        type="rect",
        x0=0,
        y0=-0.5,
        x1=33,
        y1=0.5,
        fillcolor="red",
        opacity=0.6,
        line=dict(width=0)
    )

    fig_composite.add_shape(
        type="rect",
        x0=33,
        y0=-0.5,
        x1=66,
        y1=0.5,
        fillcolor="yellow",
        opacity=0.6,
        line=dict(width=0)
    )

    fig_composite.add_shape(
        type="rect",
        x0=66,
        y1=0.5,
        x1=100,
        y0=-0.5,
        fillcolor="green",
        opacity=0.6,
        line=dict(width=0)
    )

    fig_composite.add_shape(
        type="line",
        x0=composite_score,
        y0=-0.5,
        x1=composite_score,
        y1=0.5,
        line=dict(color="Black", width=3)
    )

    fig_composite.update_layout(
        title='Composite Score',
        xaxis=dict(range=[0, 100], showgrid=False),
        yaxis=dict(showgrid=False, zeroline=False),
        showlegend=False,
        template='plotly_white',
        autosize=True,
        width=800,
        height=100,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig_composite, use_container_width=True)

    # Create a bar chart with a pointer for RSI
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Bar(
        x=[100],  # Full length of the bar
        y=[''],
        orientation='h',
        marker=dict(
            color='rgba(255, 255, 255, 0)',  # Transparent bar
            line=dict(color='black', width=2)
        )
    ))

    fig_rsi.add_shape(
        type="rect",
        x0=0,
        y0=-0.5,
        x1=30,
        y1=0.5,
        fillcolor="red",
        opacity=0.6,
        line=dict(width=0)
    )

    fig_rsi.add_shape(
        type="rect",
        x0=30,
        y0=-0.5,
        x1=70,
        y1=0.5,
        fillcolor="yellow",
        opacity=0.6,
        line=dict(width=0)
    )

    fig_rsi.add_shape(
        type="rect",
        x0=70,
        y0=-0.5,
        x1=100,
        y1=0.5,
        fillcolor="green",
        opacity=0.6,
        line=dict(width=0)
    )

    fig_rsi.add_shape(
        type="line",
        x0=normalize_value(rsi, 0, 100, inverse=True),
        y0=-0.5,
        x1=normalize_value(rsi, 0, 100, inverse=True),
        y1=0.5,
        line=dict(color="Black", width=3)
    )

    fig_rsi.update_layout(
        title='RSI Indicator',
        xaxis=dict(range=[0, 100], showgrid=False),
        yaxis=dict(showgrid=False, zeroline=False),
        showlegend=False,
        template='plotly_white',
        autosize=True,
        width=800,
        height=100,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig_rsi, use_container_width=True)

# Explanations for indicators
    st.write("""
### Indicator Explanations
- **Historical Volatility:** This measures the standard deviation of daily returns of the stock, annualized. Lower values indicate less volatility.
- **Monte Carlo Mean Price:** The average closing price of the stock.
- **MA10, MA50, MA200:** These are moving averages over 10, 50, and 200 days, respectively. They help identify trends and potential support/resistance levels.
- **RSI:** The Relative Strength Index measures the speed and change of price movements. Values below 30 indicate the stock may be oversold, while values above 70 indicate the stock may be overbought.
- **Sharpe Ratio:** This measures the risk-adjusted return of the stock. Higher values indicate better risk-adjusted performance.
""")