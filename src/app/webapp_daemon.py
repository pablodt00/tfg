# pylint: disable=redefined-outer-name, broad-exception-caught, invalid-name
import requests
import streamlit as st
import structlog

from common.config.settings import Settings

settings = Settings()

default_logger = structlog.get_logger()

COIN_NAME_TO_SYMBOL = {
    "Bitcoin": "btc",
    "Ethereum": "eth",
    "Tether": "usdt",
    "XRP": "xrp",
    "BNB": "bnb",
    "USD Coin": "usdc",
    "Solana": "sol",
    "Dogecoin": "doge",
    "Cardano": "ada",
    "Polkadot": "dot",
}

DEFAULT_COINS_DATA = {
    "Name": list(COIN_NAME_TO_SYMBOL.keys()),
    "Last Price (€)": ["-"] * len(COIN_NAME_TO_SYMBOL),
    "Price Change 1 min": ["-"] * len(COIN_NAME_TO_SYMBOL),
    "Price Change 5 mins": ["-"] * len(COIN_NAME_TO_SYMBOL),
}


def fetch_coins_data():
    try:
        response = requests.get(f"{settings.API_DAEMON_HOST}/coins/coins", timeout=10)
        response.raise_for_status()
        data = response.json()

        coins_data = {
            "Name": [coin["name"] for coin in data],
            "Last Price (€)": [coin["last_price"] for coin in data],
            "Price Change 1 min": [coin["change_1min"] for coin in data],
            "Price Change 5 mins": [coin["change_5min"] for coin in data],
        }
        return coins_data
    except Exception as e:
        st.error(f"Error fetching coins data: {str(e)}")
        return DEFAULT_COINS_DATA


def send_alert(email, coin, operator, amount, logger):
    try:
        coin_symbol = COIN_NAME_TO_SYMBOL[coin]
        payload = {
            "coin": coin_symbol,
            "amount": amount,
            "email": email,
            "condition": operator,
        }
        logger.info("Performing request to set alert", payload=payload)
        response = requests.post(
            f"{settings.API_DAEMON_HOST}/alerts/add", json=payload, timeout=10
        )
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error setting alert: {str(e)}")
        return False


st.set_page_config(page_title="Crypto Alerts Dashboard")

st.title("Crypto Alerts Dashboard - TFG")

tab1, tab2 = st.tabs(["Coins", "Alerts"])

with tab1:
    st.subheader("Cryptocurrency Prices")

    coins_data = fetch_coins_data()

    if coins_data:
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            st.dataframe(coins_data, use_container_width=True, height=200)
    else:
        st.warning("Unable to load cryptocurrency data")

with tab2:
    st.subheader("Set Price Alert")

    email = st.text_input("Email Address", placeholder="Enter your email")

    selected_coin = st.selectbox("Select Coin", list(COIN_NAME_TO_SYMBOL.keys()))

    operator = st.selectbox("Condition", [">=", "<="])

    amount = st.number_input("Alert Price", placeholder="Enter target price")

    if st.button("Set Alert"):
        if email and selected_coin and amount:
            if operator == ">=":
                operator_text = "GREATER_THAN_OR_EQUAL"
            else:
                operator_text = "LESS_THAN_OR_EQUAL"
            if send_alert(email, selected_coin, operator_text, amount, default_logger):
                st.success(
                    f"Alert set for {selected_coin} {operator} ${amount} for {email}"
                )
        else:
            st.error("Please fill in all fields")
