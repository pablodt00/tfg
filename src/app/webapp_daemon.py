import requests
import streamlit as st

st.title("TFG WebApp")

if st.button("Set alert"):
    response = requests.get("http://localhost:8000/api/endpoint", timeout=10)
    if response.ok:
        data = response.json()
        st.json(data)
    else:
        st.error("Failed to fetch data")

user_input = st.text_input("Set alert:")
if user_input:
    st.write(f"You entered: {user_input}")
