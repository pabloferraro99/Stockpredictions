import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from itertools import product

def calculate_hedge(nasdaq_value, nasdaq_leverage, nasdaq_inverse_leverage):
    nasdaq_exposure = nasdaq_value * nasdaq_leverage
    hedge_amount = nasdaq_exposure / abs(nasdaq_inverse_leverage)
    return hedge_amount

@st.cache_data
def fetch_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    data.reset_index(inplace=True)
    return data

def show_hedging_strategy():
    st.title("Hedging Strategy Calculator")

    st.subheader("Input Parameters")
    nasdaq_value = st.number_input("Value of NASDAQ ETF position (€):", value=4000.0)
    total_amount_available = st.number_input("Total amount available (€):", value=10000.0)
    max_leverage_nasdaq = st.number_input("Max leverage for NASDAQ ETF:", value=8)
    max_leverage_inverse = st.number_input("Max leverage for NASDAQ inverse ETF:", value=20)
    risk_profile = st.slider("Risk Profile (1 - Low Risk, 10 - High Risk):", 1, 10, 5)
    start_date = st.date_input("Start date:", value=pd.to_datetime("2021-04-01"))
    end_date = st.date_input("End date:", value=pd.to_datetime("today"))

    if st.button("Calculate Hedge Amount"):
        # Fetch NASDAQ data
        nasdaq_data = fetch_data('^IXIC', start_date, end_date)

        # Filter data starting from 23-Apr-2021
        nasdaq_data = nasdaq_data[nasdaq_data['Date'] >= '2021-04-23']

        # Define ranges for different leverages and hedge amounts based on risk profile
        leverage_range_nasdaq = range(1, max_leverage_nasdaq + 1)
        leverage_range_inverse = range(1, max_leverage_inverse + 1)
        hedge_amount_range = np.linspace(0.5, 2.0, 16)  # 0.5x to 2.0x the calculated hedge amount

        results = []

        for nasdaq_leverage, inverse_leverage, hedge_multiplier in product(leverage_range_nasdaq, leverage_range_inverse, hedge_amount_range):
            hedge_amount = calculate_hedge(nasdaq_value, nasdaq_leverage, inverse_leverage) * hedge_multiplier
            if (nasdaq_value + hedge_amount) > total_amount_available:
                continue
            nasdaq_data[f'NASDAQ x{nasdaq_leverage}'] = nasdaq_value * (nasdaq_data['Close'].pct_change().fillna(0) * nasdaq_leverage + 1).cumprod()
            nasdaq_data[f'NASDAQ -x{inverse_leverage}'] = hedge_amount * (nasdaq_data['Close'].pct_change().fillna(0) * -inverse_leverage + 1).cumprod()
            nasdaq_data['Total Portfolio Value'] = nasdaq_data[f'NASDAQ x{nasdaq_leverage}'] + nasdaq_data[f'NASDAQ -x{inverse_leverage}']

            final_value = nasdaq_data['Total Portfolio Value'].iloc[-1]
            max_drawdown = ((nasdaq_data['Total Portfolio Value'].cummax() - nasdaq_data['Total Portfolio Value']) / nasdaq_data['Total Portfolio Value'].cummax()).max()
            results.append({
                'nasdaq_leverage': nasdaq_leverage,
                'inverse_leverage': inverse_leverage,
                'hedge_multiplier': hedge_multiplier,
                'final_value': final_value,
                'max_drawdown': max_drawdown
            })

        results_df = pd.DataFrame(results)
        optimal_strategy = results_df.loc[results_df['final_value'].idxmax()]

        st.subheader("Optimal Strategy")
        st.write(f"Optimal NASDAQ leverage: {optimal_strategy['nasdaq_leverage']}")
        st.write(f"Optimal NASDAQ inverse leverage: {optimal_strategy['inverse_leverage']}")
        st.write(f"Optimal hedge multiplier: {optimal_strategy['hedge_multiplier']:.2f}")
        st.write(f"Final portfolio value: €{optimal_strategy['final_value']:.2f}")
        st.write(f"Max drawdown: {optimal_strategy['max_drawdown']:.2%}")

        # Recalculate the optimal strategy
        optimal_nasdaq_leverage = optimal_strategy['nasdaq_leverage']
        optimal_inverse_leverage = optimal_strategy['inverse_leverage']
        optimal_hedge_amount = calculate_hedge(nasdaq_value, optimal_nasdaq_leverage, optimal_inverse_leverage) * optimal_strategy['hedge_multiplier']

        nasdaq_data[f'NASDAQ x{optimal_nasdaq_leverage}'] = nasdaq_value * (nasdaq_data['Close'].pct_change().fillna(0) * optimal_nasdaq_leverage + 1).cumprod()
        nasdaq_data[f'NASDAQ -x{optimal_inverse_leverage}'] = optimal_hedge_amount * (nasdaq_data['Close'].pct_change().fillna(0) * -optimal_inverse_leverage + 1).cumprod()
        nasdaq_data['Total Portfolio Value'] = nasdaq_data[f'NASDAQ x{optimal_nasdaq_leverage}'] + nasdaq_data[f'NASDAQ -x{optimal_inverse_leverage}']

        # Create the plot
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=nasdaq_data['Date'], y=nasdaq_data['Close'], mode='lines', name='NASDAQ'))
        fig.add_trace(go.Scatter(x=nasdaq_data['Date'], y=nasdaq_data[f'NASDAQ x{optimal_nasdaq_leverage}'], mode='lines', name=f'NASDAQ x{optimal_nasdaq_leverage} ETF'))
        fig.add_trace(go.Scatter(x=nasdaq_data['Date'], y=nasdaq_data[f'NASDAQ -x{optimal_inverse_leverage}'], mode='lines', name=f'NASDAQ x{optimal_inverse_leverage} Inverse ETF'))
        fig.add_trace(go.Scatter(x=nasdaq_data['Date'], y=nasdaq_data['Total Portfolio Value'], mode='lines', name='Total Portfolio Value', line=dict(color='black', dash='dash')))

        fig.update_layout(
            title='Investment Comparison',
            xaxis_title='Date',
            yaxis_title='Value (€)',
            template='plotly_white',
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Add personalized explanation
        st.write(f"""
        ### Explanation of Results
        The Hedging Strategy Calculator for the NASDAQ ETF with an initial position value of €{nasdaq_value:.2f} and a total amount available of €{total_amount_available:.2f} 
        identifies the optimal hedging strategy to maximize your portfolio value while managing risk.

        **Key Parameters:**
        - **NASDAQ Leverage:** {optimal_strategy['nasdaq_leverage']}
        - **NASDAQ Inverse Leverage:** {optimal_strategy['inverse_leverage']}
        - **Hedge Multiplier:** {optimal_strategy['hedge_multiplier']:.2f}
        - **Final Portfolio Value:** €{optimal_strategy['final_value']:.2f}
        - **Max Drawdown:** {optimal_strategy['max_drawdown']:.2%}

        **Charts Explanation:**
        - The first chart displays the value of the NASDAQ, leveraged NASDAQ ETF, inverse leveraged NASDAQ ETF, and the total portfolio value over time.
        - The second chart (if applicable) would show any additional insights or comparisons based on your strategy.

        By analyzing these results, you can understand how different leverage and hedge strategies impact your portfolio and make informed decisions to optimize performance and manage risk.
        """)

if __name__ == "__main__":
    show_hedging_strategy()