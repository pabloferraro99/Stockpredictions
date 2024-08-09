import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from arch import arch_model
import statsmodels.api as sm
import scipy.stats as stats

def show_volatility_prediction():
    st.title("NASDAQ Volatility Prediction with Price")

    ticker = st.text_input("Enter the ticker symbol (e.g., ^IXIC for NASDAQ):", value="^IXIC")
    start_date = st.date_input("Start date:", value=pd.to_datetime("2021-04-01"))
    end_date = st.date_input("End date:", value=pd.to_datetime('today'))  # Default to the current day

    @st.cache_data
    def fetch_data(ticker, start, end):
        data = yf.download(ticker, start=start, end=end)
        data.reset_index(inplace=True)
        return data

    nasdaq_data = fetch_data(ticker, start_date, end_date)

    nasdaq_data['Log Returns'] = np.log(nasdaq_data['Close'] / nasdaq_data['Close'].shift(1))
    nasdaq_data.dropna(inplace=True)

    # Define a function to fit the model and return the AIC for model comparison
    def fit_garch_model(p, q):
        model = arch_model(nasdaq_data['Log Returns'], vol='Garch', p=p, q=q)
        model_fit = model.fit(disp='off')
        return model_fit.aic, model_fit

    # Hyperparameter tuning for the GARCH model
    p_values = range(1, 4)
    q_values = range(1, 4)
    best_aic = float('inf')
    best_pq = None
    best_model_fit = None

    for p in p_values:
        for q in q_values:
            aic, model_fit = fit_garch_model(p, q)
            if aic < best_aic:
                best_aic = aic
                best_pq = (p, q)
                best_model_fit = model_fit

    st.write(f"Best GARCH model order: {best_pq} with AIC: {best_aic:.2f}")

    # Fit the best GARCH model
    best_p, best_q = best_pq
    volatility = best_model_fit.conditional_volatility

    forecast_horizon = 30
    forecast = best_model_fit.forecast(horizon=forecast_horizon)
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

    fig.add_trace(go.Scatter(x=nasdaq_data['Date'], y=volatility, mode='lines', name='Historical Volatility', line=dict(color='blue')), secondary_y=False)
    fig.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Forecasted Volatility'], mode='lines', name='Forecasted Volatility', line=dict(dash='dash', color='red')), secondary_y=False)
    fig.add_trace(go.Scatter(x=nasdaq_data['Date'], y=nasdaq_data['Close'], mode='lines', name='NASDAQ Price', line=dict(color='green')), secondary_y=True)

    fig.update_layout(
        title=f'NASDAQ Volatility Prediction with Price<br>Correlation between Price and Volatility: {correlation:.2f}',
        xaxis_title='Date',
        yaxis_title='Volatility',
        yaxis2_title='NASDAQ Price',
        template='plotly_white',
        autosize=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig, use_container_width=True)

    st.write(f"Correlation between NASDAQ Price and Volatility: {correlation:.2f}")

    # Residual diagnostics
    st.subheader("Model Residual Diagnostics")
    residuals = best_model_fit.resid / best_model_fit.conditional_volatility

    # Ljung-Box test
    st.write("Ljung-Box test p-values for residuals:")
    lb_test = sm.stats.acorr_ljungbox(residuals, lags=[10], return_df=True)
    st.write(lb_test)

    # Plot standardized residuals
    fig_resid = go.Figure()
    fig_resid.add_trace(go.Scatter(x=nasdaq_data['Date'], y=residuals, mode='lines', name='Standardized Residuals', line=dict(color='purple')))
    fig_resid.update_layout(
        title='Standardized Residuals of GARCH Model',
        xaxis_title='Date',
        yaxis_title='Standardized Residuals',
        template='plotly_white',
        autosize=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_resid, use_container_width=True)

    # QQ plot of residuals using Plotly
    st.subheader("QQ Plot of Residuals")
    qq = sm.qqplot(residuals, line='s')
    qq_data = qq.gca().lines
    qq_x = qq_data[0].get_xdata()
    qq_y = qq_data[0].get_ydata()
    qq_line = qq_data[1].get_ydata()

    fig_qq = go.Figure()
    fig_qq.add_trace(go.Scatter(x=qq_x, y=qq_y, mode='markers', name='Residuals', marker=dict(color='blue')))
    fig_qq.add_trace(go.Scatter(x=qq_x, y=qq_line, mode='lines', name='QQ Line', line=dict(color='red')))
    fig_qq.update_layout(
        title='QQ Plot of Standardized Residuals',
        xaxis_title='Theoretical Quantiles',
        yaxis_title='Sample Quantiles',
        template='plotly_white',
        autosize=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_qq, use_container_width=True)

    # Histogram of residuals
    st.subheader("Histogram of Residuals")
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(x=residuals, nbinsx=50, name='Standardized Residuals', marker=dict(color='cyan')))
    fig_hist.update_layout(
        title='Histogram of Standardized Residuals',
        xaxis_title='Standardized Residuals',
        yaxis_title='Frequency',
        template='plotly_white',
        autosize=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# To use the updated function, ensure this is called in your main Streamlit app.