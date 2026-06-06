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

COIN_EMOJI = {
    "Bitcoin": "₿",
    "Ethereum": "Ξ",
    "Tether": "₮",
    "XRP": "✕",
    "BNB": "B",
    "USD Coin": "$",
    "Solana": "◎",
    "Dogecoin": "Ð",
    "Cardano": "₳",
    "Polkadot": "●",
}

DEFAULT_COINS_DATA = {
    "Moneda": list(COIN_NAME_TO_SYMBOL.keys()),
    "Último precio (€)": ["-"] * len(COIN_NAME_TO_SYMBOL),
    "Variación 1 min": ["-"] * len(COIN_NAME_TO_SYMBOL),
    "Variación 5 min": ["-"] * len(COIN_NAME_TO_SYMBOL),
}


def fetch_coins_data():
    try:
        response = requests.get(f"{settings.API_DAEMON_HOST}/coins/coins", timeout=10)
        response.raise_for_status()
        data = response.json()

        symbol_to_name = {v: k for k, v in COIN_NAME_TO_SYMBOL.items()}

        coins_data = {
            "Moneda": [
                symbol_to_name.get(coin["coin"], coin["coin"].upper()) for coin in data
            ],
            "Último precio (€)": [coin["last_price"] for coin in data],
            "Variación 1 min": [
                (
                    f"{coin['price_1_min_change_percent']}%"
                    if coin["price_1_min_change_percent"] is not None
                    else "-"
                )
                for coin in data
            ],
            "Variación 5 min": [
                (
                    f"{coin['price_5_min_change_percent']}%"
                    if coin["price_5_min_change_percent"] is not None
                    else "-"
                )
                for coin in data
            ],
        }
        return coins_data
    except Exception as e:
        st.error(f"Error al obtener los datos de monedas: {str(e)}")
        return DEFAULT_COINS_DATA


def fetch_coins_raw():
    try:
        response = requests.get(f"{settings.API_DAEMON_HOST}/coins/coins", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


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
        st.error(f"Error al crear la alerta: {str(e)}")
        return False


def _change_color(value_str: str) -> str:
    if value_str == "-":
        return "<span style='color:#888'>—</span>"
    try:
        val = float(value_str.replace("%", ""))
        color = "#2ecc71" if val >= 0 else "#e74c3c"
        arrow = "▲" if val >= 0 else "▼"
        return (
            f"<span style='color:{color};font-weight:600'>"
            f"{arrow} {abs(val):.2f}%</span>"
        )
    except ValueError:
        return value_str


st.set_page_config(
    page_title="Panel de Alertas de Criptomonedas",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        .stApp { background-color: #0e1117; }

        .dashboard-header {
            background: linear-gradient(135deg, #1a1d2e 0%, #16213e 100%);
            border-radius: 12px;
            padding: 1.5rem 2rem;
            margin-bottom: 1.5rem;
            border: 1px solid #2a2d3e;
        }
        .dashboard-header h1 {
            color: #f0b429;
            font-size: 2rem;
            margin: 0;
        }
        .dashboard-header p {
            color: #8892a4;
            margin: 0.3rem 0 0 0;
            font-size: 0.9rem;
        }

        .coin-card {
            background: #1a1d2e;
            border: 1px solid #2a2d3e;
            border-radius: 10px;
            padding: 1rem 1.2rem;
            text-align: center;
            transition: border-color 0.2s;
        }
        .coin-card:hover { border-color: #f0b429; }
        .coin-card .symbol { font-size: 1.6rem; }
        .coin-card .name { color: #8892a4; font-size: 0.75rem; margin: 0.2rem 0; }
        .coin-card .price { color: #e8eaf0; font-size: 1.1rem; font-weight: 700; }
        .coin-card .change { font-size: 0.8rem; margin-top: 0.3rem; }

        .section-title {
            color: #f0b429;
            font-size: 1.1rem;
            font-weight: 600;
            border-bottom: 1px solid #2a2d3e;
            padding-bottom: 0.4rem;
            margin-bottom: 1rem;
        }

        div[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
        .stTabs [data-baseweb="tab"] { color: #8892a4; }
        .stTabs [aria-selected="true"] { color: #f0b429 !important; }
        label { color: #c0c8d8 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="dashboard-header">
        <h1>Panel de Alertas de Criptomonedas</h1>
        <p>Precios de criptomonedas en tiempo real y alertas de precio personalizadas</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["Precios", "Crear alerta"])

with tab1:
    _, main_col, _ = st.columns([1, 10, 1])
    with main_col:
        title_col, refresh_col = st.columns([8, 1])
        with title_col:
            st.markdown(
                '<div class="section-title">Precios de criptomonedas en tiempo real (EUR)</div>',
                unsafe_allow_html=True,
            )
        with refresh_col:
            if st.button("⟳ Actualizar", use_container_width=True):
                st.rerun()

        raw_data = fetch_coins_raw()

        if raw_data:
            symbol_to_name = {v: k for k, v in COIN_NAME_TO_SYMBOL.items()}

            top5 = raw_data[:5]
            card_cols = st.columns(len(top5))
            for col, coin in zip(card_cols, top5):
                name = symbol_to_name.get(coin["coin"], coin["coin"].upper())
                last = coin["last_price"]
                price = last if isinstance(last, (int, float)) else None
                delta = coin["price_1_min_change_percent"]
                with col:
                    st.metric(
                        label=f"{COIN_EMOJI.get(name, '')} {name}".strip(),
                        value=f"€{price:,.2f}" if price is not None else "—",
                        delta=f"{delta:+.2f}% 1m" if delta is not None else None,
                    )

            st.markdown(
                '<div class="section-title" style="margin-top:1.2rem">'
                'Tabla de precios completa</div>',
                unsafe_allow_html=True,
            )

            import pandas as pd

            rows = []
            for coin in raw_data:
                name = symbol_to_name.get(coin["coin"], coin["coin"].upper())
                rows.append({
                    "Moneda": f"{COIN_EMOJI.get(name, '')} {name}".strip(),
                    "Precio (EUR)": (
                        coin["last_price"]
                        if isinstance(coin["last_price"], (int, float))
                        else None
                    ),
                    "Variación 1 min (%)": coin["price_1_min_change_percent"],
                    "Variación 5 min (%)": coin["price_5_min_change_percent"],
                })

            df = pd.DataFrame(rows)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Moneda": st.column_config.TextColumn("Moneda", width="medium"),
                    "Precio (EUR)": st.column_config.NumberColumn(
                        "Precio (EUR)", format="€%.4f", width="medium"
                    ),
                    "Variación 1 min (%)": st.column_config.NumberColumn(
                        "Variación 1 min", format="%.2f%%", width="small"
                    ),
                    "Variación 5 min (%)": st.column_config.NumberColumn(
                        "Variación 5 min", format="%.2f%%", width="small"
                    ),
                },
            )

        else:
            coins_data = fetch_coins_data()
            st.warning(
                "Datos en tiempo real no disponibles — mostrando valores en caché."
            )
            st.dataframe(coins_data, use_container_width=True)

with tab2:
    _, main_col, _ = st.columns([1, 10, 1])
    with main_col:
        st.markdown(
            '<div class="section-title">Crear una alerta de precio</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            left, right = st.columns(2)

            with left:
                email = st.text_input("Correo electrónico", placeholder="usuario@ejemplo.com")
                selected_coin = st.selectbox(
                    "Criptomoneda", list(COIN_NAME_TO_SYMBOL.keys())
                )

            with right:
                operator = st.selectbox(
                    "Condición",
                    [">=", "<="],
                    format_func=lambda x: (
                        "El precio sube hasta o supera  ≥"
                        if x == ">="
                        else "El precio baja hasta o cae por debajo de  ≤"
                    ),
                )
                amount = st.number_input(
                    "Precio objetivo (EUR)",
                    min_value=0.0,
                    step=1.0,
                    format="%.4f",
                    placeholder="p. ej. 50000.00",
                )

            st.markdown("<br>", unsafe_allow_html=True)

            btn_col, info_col = st.columns([1, 3])
            with btn_col:
                submit = st.button(
                    "Crear alerta", use_container_width=True, type="primary"
                )
            with info_col:
                st.markdown(
                    "<p style='color:#8892a4;font-size:0.85rem;margin-top:0.6rem'>"
                    "Recibirás un correo electrónico cuando se cumpla la condición de precio.</p>",
                    unsafe_allow_html=True,
                )

            if submit:
                if email and selected_coin and amount:
                    operator_text = (
                        "GREATER_THAN_OR_EQUAL"
                        if operator == ">="
                        else "LESS_THAN_OR_EQUAL"
                    )
                    if send_alert(
                        email, selected_coin, operator_text, amount, default_logger
                    ):
                        st.success(
                            f"Alerta creada. Recibirás una notificación en **{email}** cuando "
                            f"**{selected_coin}** sea **{operator} €{amount:,.4f}**"
                        )
                else:
                    st.warning("Por favor, rellena todos los campos antes de continuar.")
