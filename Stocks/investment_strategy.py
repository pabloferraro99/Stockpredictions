import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from itertools import product

def show_investment_strategy():
    st.title("Investment Strategy")

    ticker = st.text_input("Enter the ticker symbol (e.g., ^IXIC for NASDAQ):", value="^IXIC")
    start_date = st.date_input("Start date:", value=pd.to_datetime("2023-04-01"))
    end_date = st.date_input("End date:", value=pd.to_datetime("2024-06-18"))
    leverage_factor = st.number_input("Enter the leverage factor:", value=8)

    @st.cache_data
    def fetch_data(ticker, start, end):
        data = yf.download(ticker, start=start, end=end)
        data.reset_index(inplace=True)
        return data

    nasdaq_data = fetch_data(ticker, start_date, end_date)

    nasdaq_data['Log Returns'] = np.log(nasdaq_data['Close'] / nasdaq_data['Close'].shift(1))
    nasdaq_data.dropna(inplace=True)
    nasdaq_data['Leveraged Log Returns'] = nasdaq_data['Log Returns'] * leverage_factor

    initial_investment = 5000
    max_additional_investment = 15000
    scenarios = [
        {'threshold': -0.03, 'additional_investment': 300},
        {'threshold': -0.04, 'additional_investment': 300},
        {'threshold': -0.02, 'additional_investment': 200},
        {'threshold': -0.05, 'additional_investment': 100}
    ]

    def simulate_investment(threshold, additional_investment):
        total_additional_invested = 0
        cumulative_value = initial_investment
        investment_values = []
        buy_dates = []
        buy_amounts = []

        for i, row in nasdaq_data.iterrows():
            daily_return = np.exp(row['Leveraged Log Returns'])
            cumulative_value *= daily_return
            if row['Log Returns'] <= threshold and total_additional_invested < max_additional_investment:
                additional_amount = min(additional_investment, max_additional_investment - total_additional_invested)
                cumulative_value += additional_amount
                total_additional_invested += additional_amount
                buy_dates.append(row['Date'])
                buy_amounts.append(cumulative_value)
            investment_values.append(cumulative_value)

        return investment_values, buy_dates, buy_amounts

    fig = go.Figure()

    for scenario in scenarios:
        investment_values, buy_dates, buy_amounts = simulate_investment(scenario['threshold'], scenario['additional_investment'])
        scenario_label = f"Threshold={scenario['threshold']}, Add. Invest.={scenario['additional_investment']} Euros"
        fig.add_trace(go.Scatter(x=nasdaq_data['Date'], y=investment_values, mode='lines', name=scenario_label))
        fig.add_trace(go.Scatter(x=buy_dates, y=buy_amounts, mode='markers', name=f"{scenario_label} Buy Points", marker=dict(size=6)))

    fig.add_trace(go.Scatter(x=nasdaq_data['Date'], y=nasdaq_data['Close'], mode='lines', name='NASDAQ Index Value', line=dict(dash='dash')))

    fig.update_layout(
        title=f'Comparison of Different Investment Strategies in Leveraged NASDAQ ETF ({leverage_factor}x)',
        xaxis_title='Date',
        yaxis_title='Value (€)',
        template='plotly_white'
    )

    st.plotly_chart(fig)