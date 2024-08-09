import streamlit as st

# Set page configuration
st.set_page_config(page_title="Finance Dashboard", layout="wide")

from volatility_prediction import show_volatility_prediction
from investment_strategy import show_investment_strategy
from prediction import show_prediction
from streamlit_test import show_streamlit_test
from monte_carlo import show_monte_carlo_simulation
from hedging import show_hedging_strategy
from log_returns import show_log_returns
from show_investment_decision import show_investment_decision
from sector_performance import show_performance_charts  # Added import for sector performance
from best_performing_companies import show_best_performing_companies  # Added import for best-performing companies

# Custom CSS for a card-based layout
card_layout_css = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #f8f9fa;
    color: black;
    max-width: 1400px;  /* Increased from 1200px to 1400px */
    margin: 0 auto;
    padding: 2rem;
    box-sizing: border-box;
}

[data-testid="stSidebar"] {
    background-color: #d3d3d3;  /* Change sidebar color to grey */
    padding: 1rem;
    border-radius: 10px;
}

[data-testid="stSidebarNav"] ul {
    padding-left: 0;
}

[data-testid="stSidebarNav"] ul li {
    list-style: none;
    margin-bottom: 10px;
}

[data-testid="stSidebarNav"] ul li a {
    text-decoration: none;
    color: black;
    font-weight: bold;
}

[data-testid="stHeader"] {
    background-color: #ffffff;
}

.card {
    padding: 2rem;
    background: white;
    margin: 2rem auto;
    border-radius: 10px;
    box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
    max-width: 100%;
    box-sizing: border-box;
}

h1, h2, h3, h4, h5, h6 {
    color: #333;
}

input[type="text"], input[type="number"], select {
    width: 100%;
    padding: 0.5rem;
    margin: 0.5rem 0;
    box-sizing: border-box;
}

.stDateInput input {
    width: 100%;
    padding: 0.5rem;
    margin: 0.5rem 0;
    box-sizing: border-box;
}

.stButton button {
    width: 100%;
    padding: 0.5rem;
    margin: 0.5rem 0;
    box-sizing: border-box;
}

.stSlider {
    margin: 1rem 0;
}
</style>
"""
st.markdown(card_layout_css, unsafe_allow_html=True)

st.sidebar.title("Navigation")
selection = st.sidebar.selectbox("Go to", [
    "Prediction", 
    "Volatility Prediction", 
    "Investment Strategy", 
    "Portfolio Weight Optimization", 
    "Hedging Strategy",
    "Log Returns Analysis",
    "Monte Carlo Simulation",
    "Investment Decision",
    "Sector Performance",  # Added sector performance to the selection
    "Best Performing Companies"  # Added best-performing companies to the selection
])

if selection == "Prediction":
    show_prediction()
elif selection == "Volatility Prediction":
    show_volatility_prediction()
elif selection == "Investment Strategy":
    show_investment_strategy()
elif selection == "Portfolio Weight Optimization":
    show_streamlit_test()
elif selection == "Hedging Strategy":
    show_hedging_strategy()
elif selection == "Log Returns Analysis":
    show_log_returns()
elif selection == "Monte Carlo Simulation":
    show_monte_carlo_simulation()
elif selection == "Investment Decision":
    show_investment_decision()
elif selection == "Sector Performance":
    show_performance_charts()  # Call the function for sector performance
elif selection == "Best Performing Companies":
    show_best_performing_companies()  # Call the function for best-performing companies