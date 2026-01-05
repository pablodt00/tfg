import requests
import streamlit as st

from common.config.settings import Settings

settings = Settings()


def fetch_coins_data():
    try:
        response = requests.get(f"{settings.API_DAEMON_HOST}/coins/coins")
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
        return None


def send_alert(email, coin, operator, amount):
    try:
        payload = {"email": email, "coin": coin, "operator": operator, "amount": amount}
        response = requests.post(f"{settings.API_DAEMON_HOST}/alerts/add", json=payload)
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

    coins = ["Bitcoin", "Ethereum", "Cardano", "Solana"]
    selected_coin = st.selectbox("Select Coin", coins)

    operator = st.selectbox("Condition", [">=", "<="])

    amount = st.text_input("Alert Price", placeholder="Enter target price")

    if st.button("Set Alert"):
        if email and selected_coin and amount:
            if send_alert(email, selected_coin, operator, amount):
                st.success(
                    f"Alert set for {selected_coin} {operator} ${amount} for {email}"
                )
        else:
            st.error("Please fill in all fields")
