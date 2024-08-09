import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from itertools import product

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stTextInput, .stNumberInput, .stDateInput {
        margin-bottom: 20px;
    }
    .stForm {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
    }
    .stTitle {
        font-size: 32px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def show_investment_strategy():
    st.title("Investment Strategy")

    with st.form("investment_form"):
        st.subheader("General Settings")
        tickers = st.text_area("Enter ticker symbols separated by commas (e.g., ^IXIC, AAPL, MSFT):", value="^IXIC")
        leverage_factor = st.number_input("Leverage factor:", value=8)
        
        st.subheader("Date Range")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start date:", value=pd.to_datetime("2023-04-01"))
        with col2:
            end_date = st.date_input("End date:", value=pd.to_datetime("today"))

        st.subheader("Investment Parameters")
        initial_investment = st.number_input("Initial investment:", value=10000)
        max_monthly_addition = st.number_input("Maximum monthly addition:", value=1000)
        submit_button = st.form_submit_button("Run Simulation")

    if submit_button:
        @st.cache_data
        def fetch_data(ticker, start, end):
            data = yf.download(ticker, start=start, end=end)
            data.reset_index(inplace=True)
            return data

        def simulate_investment(threshold, initial_investment, monthly_addition, nasdaq_data):
            wallet = 0
            cumulative_value = initial_investment
            investment_values = []
            wallet_values = []
            buy_dates = []
            buy_amounts = []

            for i, row in nasdaq_data.iterrows():
                if row['Date'].day == 10:
                    wallet += monthly_addition

                daily_return = np.exp(row['Leveraged Log Returns'])
                cumulative_value *= daily_return
                investment_values.append(cumulative_value)
                wallet_values.append(wallet)

                if row['Log Returns'] <= threshold and wallet > 0:
                    cumulative_value += wallet
                    buy_dates.append(row['Date'])
                    buy_amounts.append(cumulative_value)
                    wallet = 0

            return cumulative_value, investment_values, wallet_values, buy_dates, buy_amounts

        # Parameter sweep settings
        threshold_values = np.arange(-0.10, 0.0, 0.01)  # More granular threshold values from -10% to 0%
        monthly_addition_values = np.arange(100, max_monthly_addition + 100, 100)  # Monthly additions from 100 to max_monthly_addition in increments of 100

        results = []

        ticker_list = [ticker.strip() for ticker in tickers.split(",")]
        for ticker in ticker_list:
            nasdaq_data = fetch_data(ticker, start_date, end_date)

            nasdaq_data['Log Returns'] = np.log(nasdaq_data['Close'] / nasdaq_data['Close'].shift(1))
            nasdaq_data.dropna(inplace=True)
            nasdaq_data['Leveraged Log Returns'] = nasdaq_data['Log Returns'] * leverage_factor

            for threshold, monthly_addition in product(threshold_values, monthly_addition_values):
                final_value, _, _, _, _ = simulate_investment(threshold, initial_investment, monthly_addition, nasdaq_data)
                results.append({
                    'Ticker': ticker,
                    'Threshold': threshold,
                    'Monthly Addition': monthly_addition,
                    'Final Value': final_value
                })

        results_df = pd.DataFrame(results)
        optimal_strategies = results_df.loc[results_df.groupby('Ticker')['Final Value'].idxmax()]

        st.subheader("Optimal Strategies for Each Stock")
        st.dataframe(optimal_strategies)

        for _, row in optimal_strategies.iterrows():
            ticker = row['Ticker']
            optimal_threshold = row['Threshold']
            optimal_monthly_addition = row['Monthly Addition']
            ending_value = row['Final Value']

            nasdaq_data = fetch_data(ticker, start_date, end_date)
            nasdaq_data['Log Returns'] = np.log(nasdaq_data['Close'] / nasdaq_data['Close'].shift(1))
            nasdaq_data.dropna(inplace=True)
            nasdaq_data['Leveraged Log Returns'] = nasdaq_data['Log Returns'] * leverage_factor

            _, investment_values, wallet_values, buy_dates, buy_amounts = simulate_investment(optimal_threshold, initial_investment, optimal_monthly_addition, nasdaq_data)

            # Calculate CAGR
            num_years = (end_date - start_date).days / 365.25
            cagr = ((ending_value / initial_investment) ** (1 / num_years)) - 1

            st.subheader(f"CAGR for {ticker}")
            st.write(f"Compound Annual Growth Rate (CAGR): {cagr:.2%}")

            fig = go.Figure()

            fig.add_trace(go.Scatter(x=nasdaq_data['Date'], y=investment_values, mode='lines', name='Investment Value'))
            fig.add_trace(go.Scatter(x=nasdaq_data['Date'], y=nasdaq_data['Close'], mode='lines', name='NASDAQ Index Value', line=dict(dash='dash')))
            fig.add_trace(go.Scatter(x=buy_dates, y=buy_amounts, mode='markers', name='Buy Points', marker=dict(size=10, color='red')))

            # Add wallet values as a bar chart on the right axis
            fig.add_trace(go.Bar(x=nasdaq_data['Date'], y=wallet_values, name='Wallet Value', yaxis='y2', opacity=0.5))

            fig.update_layout(
                title=f'Optimal Investment Strategy for {ticker} in Leveraged NASDAQ ETF ({leverage_factor}x)',
                xaxis_title='Date',
                yaxis_title='Investment Value (€)',
                yaxis2=dict(
                    title='Wallet Value (€)',
                    overlaying='y',
                    side='right'
                ),
                template='plotly_white',
                width=1200,
                height=800,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )

            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    show_investment_strategy()