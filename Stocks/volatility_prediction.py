import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from arch import arch_model

def show_volatility_prediction():
    st.title("NASDAQ Volatility Prediction with Price")

    ticker = st.text_input("Enter the ticker symbol (e.g., ^IXIC for NASDAQ):", value="^IXIC")
    start_date = st.date_input("Start date:", value=pd.to_datetime("2021-04-01"))
    end_date = st.date_input("End date:", value=pd.to_datetime("2024-06-18"))

    @st.cache_data
    def fetch_data(ticker, start, end):
        data = yf.download(ticker, start=start, end=end)
        data.reset_index(inplace=True)
        return data

    nasdaq_data = fetch_data(ticker, start_date, end_date)

    nasdaq_data['Log Returns'] = np.log(nasdaq_data['Close'] / nasdaq_data['Close'].shift(1))
    nasdaq_data.dropna(inplace=True)

    model = arch_model(nasdaq_data['Log Returns'], vol='Garch', p=1, q=1)
    model_fit = model.fit(disp='off')
    volatility = model_fit.conditional_volatility

    forecast_horizon = 30
    forecast = model_fit.forecast(horizon=forecast_horizon)
    forecast_volatility = forecast.variance.values[-1, :] ** 0.5

    last_date = nasdaq_data['Date'].iloc[-1]
    forecast_dates = pd.date_range(last_date, periods=forecast_horizon + 1, inclusive='right')
    forecast_df = pd.DataFrame({'Date': forecast_dates, 'Forecasted Volatility': forecast_volatility})

    merged_data = pd.DataFrame({
        'Date': nasdaq_data['Date'],
        'Price': nasdaq_data['Close'],
        'Volatility': volatility
    }).dropna()

    correlation = merged_data['Price'].corr(merged_data['Volatility'])

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=nasdaq_data['Date'], y=volatility, mode='lines', name='Historical Volatility'), secondary_y=False)
    fig.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Forecasted Volatility'], mode='lines', name='Forecasted Volatility', line=dict(dash='dash')), secondary_y=False)
    fig.add_trace(go.Scatter(x=nasdaq_data['Date'], y=nasdaq_data['Close'], mode='lines', name='NASDAQ Price'), secondary_y=True)

    fig.update_layout(
        title=f'NASDAQ Volatility Prediction with Price<br>Correlation between Price and Volatility: {correlation:.2f}',
        xaxis_title='Date',
        yaxis_title='Volatility',
        yaxis2_title='NASDAQ Price',
        template='plotly_white'
    )

    st.plotly_chart(fig)

    st.write(f"Correlation between NASDAQ Price and Volatility: {correlation:.2f}")