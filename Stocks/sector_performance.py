import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

def fetch_data(ticker):
    return yf.Ticker(ticker).history(period="1y")

def calculate_performance(data, period):
    start_date = (datetime.now() - timedelta(days=period)).replace(tzinfo=None)
    data.index = data.index.tz_localize(None)
    filtered_data = data.loc[start_date:]
    if len(filtered_data) < 2:
        return None
    return ((filtered_data['Close'][-1] - filtered_data['Close'][0]) / filtered_data['Close'][0]) * 100

def show_performance_charts():
    st.title("Sector Performance Over Different Periods")

    # Explanation of sectors
    st.header("Sector Explanations")
    st.write("""
    - **Technology**: Companies that produce software, hardware, or semiconductor equipment, and those that provide internet-related services.
    - **Healthcare**: Companies that provide medical services, manufacture medical equipment or drugs, provide medical insurance, or otherwise facilitate the provision of healthcare to patients.
    - **Communication Services**: Companies that facilitate communication or provide entertainment content and services.
    - **Consumer Cyclical**: Companies that produce goods and services that are discretionary, such as automotive, housing, entertainment, and retail.
    - **Basic Materials**: Companies that provide the raw materials required for other sectors, including mining, forestry, and chemical products.
    - **Industrials**: Companies that produce machinery, equipment, and supplies used in construction and manufacturing.
    - **Energy**: Companies that produce or supply energy, including oil, gas, and renewable energy sources.
    - **Financial**: Companies involved in banking, investment, insurance, and real estate.
    - **Real Estate**: Companies that develop, manage, or invest in real estate properties.
    - **Utilities**: Companies that provide essential services, such as water, electricity, and natural gas.
    - **Consumer Defensive**: Companies that produce essential goods such as food, beverages, tobacco, and household products.
    """)

    # Define the sectors and their representative ETFs
    sectors = {
        'Technology': 'XLK',
        'Healthcare': 'XLV',
        'Communication Services': 'XLC',
        'Consumer Cyclical': 'XLY',
        'Basic Materials': 'XLB',
        'Industrials': 'XLI',
        'Energy': 'XLE',
        'Financial': 'XLF',
        'Real Estate': 'XLRE',
        'Utilities': 'XLU',
        'Consumer Defensive': 'XLP'
    }

    # Periods in days
    periods = {
        '1 Week': 7,
        '2 Weeks': 14,
        '1 Month': 30,
        '3 Months': 90,
        '6 Months': 180,
        '1 Year': 365,
        'Year to Date': (datetime.now() - datetime(datetime.now().year, 1, 1)).days
    }

    # Fetch the data for each ETF
    data = {}
    for sector, ticker in sectors.items():
        data[sector] = fetch_data(ticker)

    # Calculate performance for each period
    performances = {period: {} for period in periods.keys()}
    for period_name, period_days in periods.items():
        for sector in sectors.keys():
            performance = calculate_performance(data[sector], period_days)
            if performance is not None:
                performances[period_name][sector] = performance

    # Determine the maximum absolute performance for dynamic axis range
    max_performance = max(max(abs(value) for value in performance.values()) for performance in performances.values())

    # Convert the performance dictionary to DataFrames and plot each period
    for period_name, performance in performances.items():
        performance_df = pd.DataFrame(list(performance.items()), columns=['Sector', 'Performance'])
        performance_df = performance_df.sort_values(by='Performance', ascending=False)

        # Create the horizontal bar chart
        fig = go.Figure(go.Bar(
            x=performance_df['Performance'],
            y=performance_df['Sector'],
            orientation='h',
            marker=dict(
                color=performance_df['Performance'],
                colorscale=[
                    [0, 'rgba(255, 0, 0, 0.6)'],  # Red with reduced opacity for negative values
                    [0.5, 'rgba(255, 0, 0, 0.6)'],  # Red with reduced opacity for negative values
                    [0.5, 'rgba(0, 255, 0, 0.6)'],  # Green with reduced opacity for positive values
                    [1, 'rgba(0, 255, 0, 0.6)']  # Green with reduced opacity for positive values
                ],
                cmin=-1,
                cmax=1
            ),
            text=[f'{val:+.2f}%' for val in performance_df['Performance']],
            textposition='outside',
            textfont=dict(color='grey')  # Change the text color to grey
        ))

        # Customize layout
        fig.update_layout(
            title=f'{period_name} Performance',
            xaxis=dict(title='Percentage', showgrid=False, zeroline=True, zerolinecolor='grey', zerolinewidth=2, color='black', range=[-max_performance, max_performance]),
            yaxis=dict(title='', showgrid=False, zeroline=False, color='white'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            bargap=0.15,
        )

        # Display the plot
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    show_performance_charts()