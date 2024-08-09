import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

def fetch_tickers_in_sector(sector):
    # Define the representative ticker for the sector and their respective company names
    sector_tickers = {
        'Technology': [('AAPL', 'Apple Inc.'), ('MSFT', 'Microsoft Corp.'), ('GOOGL', 'Alphabet Inc.'), ('NVDA', 'NVIDIA Corp.'), ('INTC', 'Intel Corp.'), ('ADBE', 'Adobe Inc.'), ('CSCO', 'Cisco Systems'), ('ORCL', 'Oracle Corp.'), ('IBM', 'IBM Corp.'), ('HPQ', 'HP Inc.')],
        'Healthcare': [('JNJ', 'Johnson & Johnson'), ('PFE', 'Pfizer Inc.'), ('MRK', 'Merck & Co.'), ('UNH', 'UnitedHealth Group'), ('ABBV', 'AbbVie Inc.'), ('TMO', 'Thermo Fisher Scientific'), ('DHR', 'Danaher Corp.'), ('BMY', 'Bristol-Myers Squibb'), ('ABT', 'Abbott Laboratories'), ('AMGN', 'Amgen Inc.')],
        'Communication Services': [('META', 'Meta Platforms'), ('GOOG', 'Alphabet Inc.'), ('NFLX', 'Netflix Inc.'), ('DIS', 'The Walt Disney Co.'), ('CMCSA', 'Comcast Corp.'), ('VZ', 'Verizon Communications'), ('T', 'AT&T Inc.'), ('TMUS', 'T-Mobile US'), ('CHTR', 'Charter Communications'), ('ATVI', 'Activision Blizzard')],
        'Consumer Cyclical': [('AMZN', 'Amazon.com Inc.'), ('TSLA', 'Tesla Inc.'), ('HD', 'The Home Depot'), ('NKE', 'Nike Inc.'), ('MCD', 'McDonald\'s Corp.'), ('SBUX', 'Starbucks Corp.'), ('BKNG', 'Booking Holdings'), ('LOW', 'Lowe\'s Companies'), ('TJX', 'TJX Companies'), ('GM', 'General Motors')],
        'Basic Materials': [('LIN', 'Linde PLC'), ('BHP', 'BHP Group'), ('RIO', 'Rio Tinto'), ('APD', 'Air Products and Chemicals'), ('ECL', 'Ecolab Inc.'), ('SHW', 'Sherwin-Williams'), ('NUE', 'Nucor Corp.'), ('FCX', 'Freeport-McMoRan'), ('DOW', 'Dow Inc.'), ('PPG', 'PPG Industries')],
        'Industrials': [('BA', 'Boeing Co.'), ('HON', 'Honeywell International'), ('GE', 'General Electric'), ('MMM', '3M Co.'), ('CAT', 'Caterpillar Inc.'), ('UPS', 'United Parcel Service'), ('UNP', 'Union Pacific'), ('RTX', 'Raytheon Technologies'), ('LMT', 'Lockheed Martin'), ('DE', 'Deere & Co.')],
        'Energy': [('XOM', 'Exxon Mobil Corp.'), ('CVX', 'Chevron Corp.'), ('COP', 'ConocoPhillips'), ('PSX', 'Phillips 66'), ('SLB', 'Schlumberger Ltd.'), ('VLO', 'Valero Energy'), ('EOG', 'EOG Resources'), ('OXY', 'Occidental Petroleum'), ('HAL', 'Halliburton Co.'), ('PXD', 'Pioneer Natural Resources')],
        'Financial': [('JPM', 'JPMorgan Chase & Co.'), ('BAC', 'Bank of America'), ('WFC', 'Wells Fargo & Co.'), ('C', 'Citigroup Inc.'), ('GS', 'Goldman Sachs'), ('MS', 'Morgan Stanley'), ('AXP', 'American Express'), ('USB', 'U.S. Bancorp'), ('PNC', 'PNC Financial Services'), ('BK', 'Bank of New York Mellon')],
        'Real Estate': [('PLD', 'Prologis Inc.'), ('AMT', 'American Tower Corp.'), ('CCI', 'Crown Castle International'), ('EQIX', 'Equinix Inc.'), ('PSA', 'Public Storage'), ('SPG', 'Simon Property Group'), ('O', 'Realty Income Corp.'), ('SBAC', 'SBA Communications'), ('WY', 'Weyerhaeuser Co.'), ('VTR', 'Ventas Inc.')],
        'Utilities': [('NEE', 'NextEra Energy'), ('DUK', 'Duke Energy'), ('SO', 'Southern Co.'), ('D', 'Dominion Energy'), ('EXC', 'Exelon Corp.'), ('AEP', 'American Electric Power'), ('SRE', 'Sempra Energy'), ('XEL', 'Xcel Energy'), ('ED', 'Consolidated Edison'), ('ES', 'Eversource Energy')],
        'Consumer Defensive': [('PG', 'Procter & Gamble'), ('KO', 'Coca-Cola Co.'), ('PEP', 'PepsiCo Inc.'), ('WMT', 'Walmart Inc.'), ('COST', 'Costco Wholesale Corp.'), ('PM', 'Philip Morris International'), ('MO', 'Altria Group'), ('KMB', 'Kimberly-Clark'), ('CL', 'Colgate-Palmolive'), ('STZ', 'Constellation Brands')]
    }
    return sector_tickers.get(sector, [])

def calculate_company_performance(ticker, period):
    data = yf.Ticker(ticker).history(period="1y")
    start_date = (datetime.now() - timedelta(days=period)).replace(tzinfo=None)
    data.index = pd.to_datetime(data.index).tz_localize(None)  # Ensure the index is timezone-naive
    filtered_data = data.loc[start_date:]
    if len(filtered_data) < 2:
        return None
    return ((filtered_data['Close'][-1] - filtered_data['Close'][0]) / filtered_data['Close'][0]) * 100

def show_best_performing_companies():
    st.title("Best and Worst Performing Companies per Sector")

    sectors = [
        'Technology', 'Healthcare', 'Communication Services', 'Consumer Cyclical',
        'Basic Materials', 'Industrials', 'Energy', 'Financial', 'Real Estate',
        'Utilities', 'Consumer Defensive'
    ]

    period = st.selectbox("Select the period for performance calculation:", ['1 Week', '2 Weeks', '1 Month', '3 Months', '6 Months', '1 Year'])

    period_days = {
        '1 Week': 7,
        '2 Weeks': 14,
        '1 Month': 30,
        '3 Months': 90,
        '6 Months': 180,
        '1 Year': 365
    }[period]

    for sector in sectors:
        st.header(f"{sector} Sector")
        tickers = fetch_tickers_in_sector(sector)
        performances = []

        for ticker, company_name in tickers:
            performance = calculate_company_performance(ticker, period_days)
            if performance is not None:
                performances.append((company_name, performance))

        performances.sort(key=lambda x: x[1], reverse=True)

        # Create a DataFrame for the best and worst performing companies
        performance_df = pd.DataFrame(performances, columns=['Company', 'Performance'])

        # Determine the range for the x-axis
        min_performance = performance_df['Performance'].min()
        max_performance = performance_df['Performance'].max()
        range_padding = (max_performance - min_performance) * 0.1  # Add 10% padding on each side
        x_range = [min_performance - range_padding, max_performance + range_padding]

        # Create the horizontal bar chart
        fig = go.Figure(go.Bar(
            x=performance_df['Performance'],
            y=performance_df['Company'],
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
            textfont=dict(color='grey')  # Change the text color to black
        ))

        
        # Customize layout
        fig.update_layout(
            title=f'Best and Worst Performing Companies in {sector} ({period})',
            xaxis=dict(title='Percentage', showgrid=False, zeroline=True, zerolinecolor='grey', zerolinewidth=2, color='black', range=x_range),
            yaxis=dict(title='', showgrid=False, zeroline=False, color='black'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='black'),
            bargap=0.15,
        )

        # Display the plot
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    show_best_performing_companies()