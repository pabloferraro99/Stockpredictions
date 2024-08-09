import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from cvxopt import matrix, solvers
import plotly.graph_objects as go

def fetch_stock_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)
    return data['Adj Close']

def calculate_returns_and_covariance(data):
    returns = data.pct_change().dropna()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    return returns, mean_returns, cov_matrix

def optimize_portfolio(mean_returns, cov_matrix, risk_factor):
    n = len(mean_returns)
    risk_factor = max(1, min(risk_factor, 10))
    adjusted_cov_matrix = cov_matrix * (10 - risk_factor) / 9.0
    adjusted_mean_returns = mean_returns * risk_factor / 10.0
    P = matrix(adjusted_cov_matrix.values)
    q = matrix(-adjusted_mean_returns.values)
    G = matrix(-np.eye(n))
    h = matrix(np.zeros(n))
    A = matrix(1.0, (1, n))
    b = matrix(1.0)
    solvers.options['show_progress'] = False
    sol = solvers.qp(P, q, G, h, A, b)
    weights = np.array(sol['x']).flatten()
    return weights

def calculate_leveraged_portfolio_value(data, weights, leverage_factor, initial_investment):
    portfolio_returns = (data.pct_change().dropna() * weights).sum(axis=1)
    leveraged_returns = portfolio_returns * leverage_factor
    portfolio_value = initial_investment * (1 + leveraged_returns).cumprod()
    return portfolio_value

def show_streamlit_test():
    st.title('Portfolio Weight Optimization')
    tickers = st.text_input('Enter ticker symbols separated by commas:', 'AAPL,MSFT,GOOGL,AMZN,TSLA')
    start_date = st.date_input('Start date:', value=pd.to_datetime('2023-01-01'))
    end_date = st.date_input('End date:', value=pd.to_datetime('today'))  # Set the default end date to today
    risk_factor = st.slider('Select your risk factor (1-10):', 1, 10, 5)
    leverage_factor = st.slider('Select your leverage factor (1-10):', 1, 10, 1)
    initial_investment = st.number_input('Enter your initial investment amount (€):', min_value=1000, step=1000, value=10000)

    tickers = [ticker.strip() for ticker in tickers.split(',')]
    data = fetch_stock_data(tickers, start_date, end_date)

    if not data.empty:
        returns, mean_returns, cov_matrix = calculate_returns_and_covariance(data)
        weights = optimize_portfolio(mean_returns, cov_matrix, risk_factor)

        st.write('Optimized Portfolio Weights:')
        for ticker, weight in zip(tickers, weights):
            st.write(f'{ticker}: {weight:.2%}')

        portfolio_value = calculate_leveraged_portfolio_value(data, weights, leverage_factor, initial_investment)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=portfolio_value.index, y=portfolio_value.values, mode='lines', name=f'Portfolio Value with {leverage_factor}x Leverage'))
        fig.update_layout(
            title='Leveraged Portfolio Performance Over Time', 
            xaxis_title='Date', 
            yaxis_title='Portfolio Value (€)',
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

        fig = go.Figure()
        fig.add_trace(go.Bar(x=tickers, y=weights, name='Weights'))
        fig.update_layout(
            title='Optimized Portfolio Weights', 
            xaxis_title='Tickers', 
            yaxis_title='Weights',
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Add personalized explanation
        st.write(f"""
        ### Explanation of Results
        The Portfolio Weight Optimization for the selected tickers ({', '.join(tickers)}) from {start_date} to {end_date} 
        shows how you can allocate your investment based on the specified risk and leverage factors.

        **Key Parameters:**
        - **Risk Factor:** {risk_factor}
        - **Leverage Factor:** {leverage_factor}
        - **Initial Investment:** €{initial_investment}

        **Charts Explanation:**
        - The first chart displays the performance of the leveraged portfolio over time. The y-axis shows the portfolio value in euros, 
          and the x-axis represents the dates within the specified range.
        - The second chart shows the optimized weights for each ticker in the portfolio. The y-axis indicates the weights, 
          and the x-axis lists the ticker symbols.

        By analyzing these results, you can understand how different weights and leverage factors affect your portfolio's performance 
        and make informed investment decisions.
        """)
    else:
        st.write('No data available for the selected tickers and date range.')

# To use the updated function, ensure this is called in your main Streamlit app.