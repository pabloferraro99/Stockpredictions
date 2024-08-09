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
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig, use_container_width=True)

    final_prices = [sim[-1] for sim in simulations]
    fig2 = px.histogram(final_prices, nbins=100, title="Final Price Distribution")
    fig2.update_layout(
        xaxis_title="Price",
        yaxis_title="Frequency",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig2, use_container_width=True)

    return final_prices

def show_monte_carlo_simulation():
    st.title("Monte Carlo Simulation")

    ticker = st.text_input("Enter the ticker symbol (e.g., NVDA for NVIDIA):", value="^IXIC")
    days_to_simulate = st.number_input("Number of days to simulate:", min_value=1, max_value=365, value=30)
    num_simulations = st.number_input("Number of simulations:", min_value=1, max_value=10000, value=1000)

    if st.button("Run Simulation"):
        simulations, last_price = monte_carlo_simulation(ticker, days_to_simulate, num_simulations)
        final_prices = plot_monte_carlo_simulation(simulations, last_price, days_to_simulate)

        # Calculate statistics
        mean_final_price = np.mean(final_prices)
        median_final_price = np.median(final_prices)
        std_final_price = np.std(final_prices)

        st.write(f"""
        ### Simulation Output Explanation
        The Monte Carlo simulation for **{ticker}** with **{num_simulations}** simulations over **{days_to_simulate}** days shows various potential future paths for the stock price. 
        
        **Key Statistics:**
        - **Mean Final Price:** {mean_final_price:.2f}
        - **Median Final Price:** {median_final_price:.2f}
        - **Standard Deviation of Final Prices:** {std_final_price:.2f}

        **Charts Explanation:**
        - The first chart displays the simulated price trajectories. Each blue line represents a possible future path of the stock price over the simulation period.
        - The second chart is a histogram showing the distribution of the final prices at the end of the simulation period. This distribution provides insights into the potential range and likelihood of different future prices, helping to understand the potential risks and returns.

        By analyzing these results, you can get a sense of the stock's potential future performance and make more informed investment decisions.
        """)

# To use the updated function, ensure this is called in your main Streamlit app.

if __name__ == "__main__":
    show_monte_carlo_simulation()