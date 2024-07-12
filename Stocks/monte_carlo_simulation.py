# monte_carlo.py

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px

def monte_carlo_simulation(ticker, days_to_simulate=30, num_simulations=1000):
    # Fetch stock data from yfinance
    data = yf.download(ticker, period="5y")
    
    # Calculate daily log returns
    data['Log Returns'] = np.log(data['Close'] / data['Close'].shift(1))
    data.dropna(inplace=True)
    
    # Calculate mean and standard deviation of log returns
    mu = data['Log Returns'].mean()
    sigma = data['Log Returns'].std()

    # Perform Monte Carlo simulation
    simulations = []
    last_price = data['Close'].iloc[-1]

    for _ in range(num_simulations):
        prices = [last_price]
        for _ in range(days_to_simulate):
            shock = np.random.normal(mu, sigma)
            price = prices[-1] * np.exp(shock)
            prices.append(price)
        simulations.append(prices)

    return simulations, last_price

def plot_monte_carlo_simulation(simulations, last_price, days_to_simulate):
    fig = go.Figure()

    for result in simulations:
        fig.add_trace(go.Scatter(x=list(range(days_to_simulate+1)), y=result, mode='lines', line=dict(color='blue', dash='solid', width=0.5), opacity=0.1))
    
    fig.update_layout(
        title=f"Monte Carlo Simulation: Stock Price Prediction",
        xaxis_title="Days",
        yaxis_title="Price",
        showlegend=False
    )

    st.plotly_chart(fig)

    final_prices = [sim[-1] for sim in simulations]
    fig2 = px.histogram(final_prices, nbins=100, title="Final Price Distribution")
    fig2.update_layout(xaxis_title="Price", yaxis_title="Frequency")

    st.plotly_chart(fig2)

def show_monte_carlo_simulation():
    st.title("Monte Carlo Simulation")

    ticker = st.text_input("Enter the ticker symbol (e.g., NVDA for NVIDIA):", value="^IXIC")
    days_to_simulate = st.number_input("Number of days to simulate:", min_value=1, max_value=365, value=30)
    num_simulations = st.number_input("Number of simulations:", min_value=1, max_value=10000, value=1000)

    if st.button("Run Simulation"):
        simulations, last_price = monte_carlo_simulation(ticker, days_to_simulate, num_simulations)
        plot_monte_carlo_simulation(simulations, last_price, days_to_simulate)
