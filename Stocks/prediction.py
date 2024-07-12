import streamlit as st
import pandas as pd
import yfinance as yf
from prophet import Prophet
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
    model.fit(prophet_df)

    # Create a DataFrame for future dates
    future_dates = model.make_future_dataframe(periods=12, freq='M')  # Predict for the next 12 months

    # Predict the future values
    forecast = model.predict(future_dates)

    # Plot the forecast using Plotly
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Predicted Price'))
    fig_forecast.add_trace(go.Scatter(x=prophet_df['ds'], y=prophet_df['y'], mode='lines', name='Actual Price'))
    fig_forecast.update_layout(title='Stock Price Forecast', xaxis_title='Date', yaxis_title='Stock Close Value')
    st.plotly_chart(fig_forecast)

    # Display the forecasted values
    st.write(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(12))

    # Extract and plot seasonality components using Prophet's plot_components method
    fig_components = model.plot_components(forecast)

    # Plot the seasonality components using Plotly
    fig = make_subplots(rows=2, cols=1, subplot_titles=("Weekly Seasonality", "Yearly Seasonality"))

    # Weekly seasonality
    weekly_data = fig_components.axes[1].lines[0].get_data()
    fig.add_trace(go.Scatter(x=weekly_data[0], y=weekly_data[1], mode='lines', name='Weekly Seasonality'), row=1, col=1)

    # Yearly seasonality
    yearly_data = fig_components.axes[2].lines[0].get_data()
    fig.add_trace(go.Scatter(x=yearly_data[0], y=yearly_data[1], mode='lines', name='Yearly Seasonality'), row=2, col=1)

    fig.update_layout(height=800, title_text="Seasonality Components")
    st.plotly_chart(fig)

# Streamlit app
st.sidebar.title("Navigation")
page = st.sidebar.selectbox('Go to', ['Prediction'])

if page == 'Prediction':
    show_prediction()
