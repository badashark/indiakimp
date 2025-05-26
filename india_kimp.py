import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="India Crypto Premium", layout="centered")
st_autorefresh(interval=60 * 1000, key="auto-refresh")
st.title("🇮🇳 인도 USDT 프리미엄 실시간 트래커")
st.caption("⏱️ 60초마다 자동 갱신됩니다.")

def get_usdt_price_inr():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "asset": "USDT",
        "fiat": "INR",
        "tradeType": "SELL",
        "page": 1,
        "rows": 10,
        "payTypes": [],
        "publisherType": None
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers).json()
    prices = [float(ad["adv"]["price"]) for ad in response["data"]]
    return min(prices)

def get_usd_inr():
    url = "https://api.frankfurter.app/latest?from=USD&to=INR"
    return requests.get(url).json()['rates']['INR']

def calculate_premium():
    local = get_usdt_price_inr()
    fx = get_usd_inr()
    global_price = 1.0
    usd_equiv = local / fx
    premium = (usd_equiv - global_price) / global_price * 100
    return round(local, 2), round(fx, 2), round(premium, 2)

usdt_inr, usd_inr, premium = calculate_premium()

st.metric("📌 인도 P2P USDT 최저가 (INR)", f"₹{usdt_inr}")
st.metric("📌 USD/INR 환율", f"₹{usd_inr}")
st.metric("💹 인도 프리미엄", f"{premium}%")
