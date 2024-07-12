import streamlit as st
import pandas as pd
import yfinance as yf
from prophet import Prophet
import matplotlib.pyplot as plt
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="Finance Dashboard", layout="wide")

# Function to show prediction
def show_prediction():
    st.title("Stock Prediction and Seasonality")

    ticker = st.text_input("Enter the ticker symbol (e.g., NVDA for NVIDIA):", value="NVDA")
    start_date = st.date_input("Start date:", value=pd.to_datetime("2019-04-01"))
    end_date = st.date_input("End date:", value=pd.to_datetime("2024-07-04"))

    @st.cache_data
    def fetch_data(ticker, start, end):
        data = yf.download(ticker, start=start, end=end)
        data.reset_index(inplace=True)
        return data

    nasdaq_data = fetch_data(ticker, start_date, end_date)

    # Filter the data to include only values starting from the start date
    filtered_nasdaq_data = nasdaq_data[nasdaq_data['Date'] >= pd.to_datetime(start_date)]

    # Prepare the data for Prophet
    prophet_df = filtered_nasdaq_data[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})

    # Initialize and fit the Prophet model
    model = Prophet()
    model.fit(prophet_df)

    # Create a DataFrame for future dates
    future_dates = model.make_future_dataframe(periods=12, freq='M')  # Predict for the next 12 months

    # Predict the future values
    forecast = model.predict(future_dates)

    # Plot the forecast
    fig1, ax1 = plt.subplots()
    model.plot(forecast, ax=ax1)
    ax1.set_title('Stock Price Forecast')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Stock Close Value')
    plt.grid(True)
    st.pyplot(fig1)

    # Display the forecasted values
    st.write(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(12))

    # Plot seasonality components
    fig2 = model.plot_components(forecast)
    st.pyplot(fig2)

# Streamlit app
st.sidebar.title("Navigation")
page = st.sidebar.selectbox('Go to', ['Prediction'])

if page == 'Prediction':
    show_prediction()
