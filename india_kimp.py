import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=60 * 1000, key="auto-refresh")
st.set_page_config(page_title="India Crypto Premium", layout="centered")
st.title("🇮🇳 인도 코인 프리미엄 실시간 트래커")
st.caption("⏱️ 60초마다 자동 갱신됩니다.")

# 1. P2P 가격 수집
def get_p2p_price_inr(coin):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {
        "asset": coin,
        "fiat": "INR",
        "tradeType": "SELL",
        "page": 1,
        "rows": 10,
        "payTypes": [],
        "publisherType": None
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers).json()
        prices = [float(ad["adv"]["price"]) for ad in response["data"]]
        return min(prices)
    except:
        return None

# 2. 글로벌 가격 수집 (USDT 기준)
def get_global_price_usdt(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
    try:
        response = requests.get(url).json()
        return float(response['price'])
    except:
        return None

# 3. USD/INR 환율
def get_usd_inr():
    try:
        url = "https://api.frankfurter.app/latest?from=USD&to=INR"
        return requests.get(url).json()['rates']['INR']
    except:
        return None

# 4. 프리미엄 계산
def calculate_premium(p2p_inr, global_usd, fx):
    if p2p_inr and global_usd and fx:
        inr_to_usd = p2p_inr / fx
        premium = (inr_to_usd - global_usd) / global_usd * 100
        return round(premium, 2)
    return None

# === 데이터 수집 ===
fx = get_usd_inr()

# USDT
p2p_usdt = get_p2p_price_inr("USDT")
global_usdt = 1.0
premium_usdt = calculate_premium(p2p_usdt, global_usdt, fx)

# BTC
p2p_btc = get_p2p_price_inr("BTC")
global_btc = get_global_price_usdt("BTC")
premium_btc = calculate_premium(p2p_btc, global_btc, fx)

# ETH
p2p_eth = get_p2p_price_inr("ETH")
global_eth = get_global_price_usdt("ETH")
premium_eth = calculate_premium(p2p_eth, global_eth, fx)

# === 출력 ===
st.subheader("📌 USD/INR 환율")
st.write(f"₹{fx}")

st.markdown("---")
st.subheader("💵 USDT 프리미엄")
st.metric("P2P 가격 (INR)", f"₹{p2p_usdt}")
st.metric("글로벌 가격 ($)", f"${global_usdt}")
st.metric("프리미엄", f"{premium_usdt}%")

st.markdown("---")
st.subheader("🟠 BTC 프리미엄")
st.metric("P2P 가격 (INR)", f"₹{p2p_btc:,}")
st.metric("글로벌 가격 ($)", f"${global_btc:,}")
st.metric("프리미엄", f"{premium_btc}%")

st.markdown("---")
st.subheader("🟣 ETH 프리미엄")
st.metric("P2P 가격 (INR)", f"₹{p2p_eth:,}")
st.metric("글로벌 가격 ($)", f"${global_eth:,}")
st.metric("프리미엄", f"{premium_eth}%")
