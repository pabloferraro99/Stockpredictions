import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

def show_log_returns():
    st.title('📈 Stock Analysis')

    # Inputs for the stock ticker, date range, and number of consecutive days
    stock_ticker = st.text_input('Enter Stock Ticker', value='^GSPC')
    start_date = st.date_input('Start Date', value=pd.to_datetime('2011-04-01'))
    end_date = st.date_input('End Date', value=pd.to_datetime('today'))
    consecutive_days = st.number_input('Number of Consecutive Days', min_value=1, value=2, step=1)

    # Fetch stock data from yfinance
    stock_data = yf.download(stock_ticker, start=start_date, end=end_date)

    # Reset index to have date as a column
    stock_data.reset_index(inplace=True)

    # Calculate daily logarithmic returns
    stock_data['Log Returns'] = np.log(stock_data['Close'] / stock_data['Close'].shift(1))

    # Drop the first row with NaN value
    stock_data.dropna(inplace=True)

    # Plot the log returns using Plotly
    fig = go.Figure()

    # Add the log returns data
    fig.add_trace(go.Scatter(x=stock_data['Date'], y=stock_data['Log Returns'], mode='lines', name='Log Returns'))

    # Customize the layout to fill the page width
    fig.update_layout(
        title=f'{stock_ticker} Daily Logarithmic Returns',
        xaxis_title='Date',
        yaxis_title='Log Returns',
        template='plotly_white',
        autosize=True,
        width=1600,
        height=800,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # Display the plot
    st.plotly_chart(fig, use_container_width=True)

    # Calculate daily returns (close-to-close)
    stock_data['Daily Return'] = stock_data['Close'].diff()

    # Identify days with positive and negative returns
    stock_data['Up'] = stock_data['Daily Return'] > 0
    stock_data['Down'] = stock_data['Daily Return'] < 0

    # Function to calculate the probability of consecutive days
    def calculate_consecutive_days(data, column, days):
        consecutive_days_column = f'Consecutive {days} Days {column}'
        data[consecutive_days_column] = data[column]
        for i in range(1, days):
            data[consecutive_days_column] &= data[column].shift(i)
        return data[consecutive_days_column].sum() / (len(data) - days + 1)

    # Calculate probabilities
    probability_up_days = calculate_consecutive_days(stock_data, 'Up', consecutive_days)
    probability_down_days = calculate_consecutive_days(stock_data, 'Down', consecutive_days)

    # Analyze volatility
    volatility = stock_data['Log Returns'].std()
    volatility_frequency = stock_data['Log Returns'].apply(lambda x: abs(x) > volatility).mean()

    # Determine the usual trend of the log returns
    mean_log_return = stock_data['Log Returns'].mean()
    trend = '📈 positive' if mean_log_return > 0 else '📉 negative'

    # Rescale volatility to a 0-100 range
    rescaled_volatility = volatility * 2000  # Adjusted to fit within 0-100 range

    # Create a color gradient bar for volatility using Plotly
    fig_volatility = go.Figure()

    fig_volatility.add_trace(go.Indicator(
        mode="gauge+number",
        value=rescaled_volatility,
        title={'text': "Volatility Grading"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "black"},
            'steps': [
                {'range': [0, 33], 'color': 'green'},
                {'range': [33, 66], 'color': 'yellow'},
                {'range': [66, 100], 'color': 'red'}],
            'threshold': {
                'line': {'color': "rgba(0, 0, 0, 0.5)", 'width': 4},  # Adjusted opacity here
                'thickness': 0.65,
                'value': rescaled_volatility}}))

    fig_volatility.update_layout(
        autosize=True,
        width=800,
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="black")
    )

    st.plotly_chart(fig_volatility, use_container_width=True)

    # Add personalized insights with color grading for volatility
    st.write(f"""
    ### 🔍 Insights from the Analysis
    - **Stock Ticker:** {stock_ticker}
    - **📅 Date Range:** From {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
    - **🔢 Number of Consecutive Days Analyzed:** {consecutive_days}
    - **📈 Probability of {consecutive_days} Consecutive Up Days:** {probability_up_days * 100:.2f}% 🚀
    - **📉 Probability of {consecutive_days} Consecutive Down Days:** {probability_down_days * 100:.2f}% 📉

    **⚠️ Volatility Analysis:**
    - **Overall Volatility (Risk):** {volatility:.4f}
    - **Frequency of High Volatility Days (Log Returns > 1 Std. Dev):** {volatility_frequency:.4f} 🔄
    - **Usual Trend of Log Returns:** The average log return is {mean_log_return:.4f}, indicating a {trend} trend over the analyzed period.

    **📊 Chart Explanation:**
    - The chart above displays the daily logarithmic returns for {stock_ticker} over the selected date range.
    - The x-axis represents the date, and the y-axis shows the logarithmic returns.
    - The fluctuations in the chart indicate the volatility of the stock returns on a daily basis.

    **💡 Statistical Insights:**
    - The calculated probabilities provide insights into the likelihood of the stock experiencing consecutive up or down days.
    - A higher probability of consecutive up days suggests a bullish trend, while a higher probability of consecutive down days indicates a bearish trend.
    - The overall volatility and frequency of high volatility days help in understanding the risk associated with the stock.
    - These probabilities and volatility measures can be useful for making informed trading or investment decisions based on the stock's historical performance.

    By analyzing these results, you can better understand the behavior of {stock_ticker} and make more informed investment decisions. 📊
    """, unsafe_allow_html=True)

# To use the updated function, ensure this is called in your main Streamlit app.