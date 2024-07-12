# streamlit_app.py

import streamlit as st
from volatility_prediction import show_volatility_prediction
from investment_strategy import show_investment_strategy
from prediction import show_prediction
from streamlit_test import show_streamlit_test
from monte_carlo import show_monte_carlo_simulation  # Ensure correct import

st.set_page_config(page_title="Finance Dashboard", layout="wide")

st.sidebar.title("Navigation")
selection = st.sidebar.selectbox("Go to", ["Volatility Prediction", "Investment Strategy", "Prediction", "Portfolio Weight Optimization", "Monte Carlo Simulation"])

if selection == "Volatility Prediction":
    show_volatility_prediction()
elif selection == "Investment Strategy":
    show_investment_strategy()
elif selection == "Prediction":
    show_prediction()
elif selection == "Portfolio Weight Optimization":
    show_streamlit_test()
elif selection == "Monte Carlo Simulation":
    show_monte_carlo_simulation()