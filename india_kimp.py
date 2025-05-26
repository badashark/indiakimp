import streamlit as st
import requests
import time
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Streamlit page config
st.set_page_config(page_title="India Crypto Premium Tracker", layout="centered")
st_autorefresh(interval=60 * 1000, key="auto-refresh")

st.title("🇮🇳 India Crypto Premium Tracker")
st.caption("Auto-updated every 60 seconds (USDT / BTC / ETH)")

# Safe JSON request function
def safe_get_json(url, retries=5, delay=3):
    for _ in range(retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            time.sleep(delay)
    return None

# P2P price (INR) from Binance
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
        response = requests.post(url, json=payload, headers=headers, timeout=5).json()
        prices = [float(ad["adv"]["price"]) for ad in response["data"]]
        return min(prices)
    except:
        return None

# Global price (USD) from CoinGecko (coin-by-coin)
def get_global_price_usdt(symbol):
    symbol_map = {
        "BTC": "bitcoin",
        "ETH": "ethereum"
    }
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol_map[symbol]}&vs_currencies=usd"
        data = safe_get_json(url)
        return float(data[symbol_map[symbol]]["usd"])
    except:
        return None

# USD/INR exchange rate
def get_usd_inr():
    url = "https://open.er-api.com/v6/latest/USD"
    data = safe_get_json(url)
    try:
        return data["rates"]["INR"]
    except:
        return None

# Premium calculation
def calculate_premium(p2p_inr, global_usd, fx):
    if p2p_inr is not None and global_usd is not None and fx is not None:
        inr_to_usd = p2p_inr / fx
        premium = (inr_to_usd - global_usd) / global_usd * 100
        return round(premium, 2)
    return None

# Fetch all data
fx = get_usd_inr()

p2p_usdt = get_p2p_price_inr("USDT")
global_usdt = 1.0
premium_usdt = calculate_premium(p2p_usdt, global_usdt, fx)

p2p_btc = get_p2p_price_inr("BTC")
global_btc = get_global_price_usdt("BTC")
premium_btc = calculate_premium(p2p_btc, global_btc, fx)

p2p_eth = get_p2p_price_inr("ETH")
global_eth = get_global_price_usdt("ETH")
premium_eth = calculate_premium(p2p_eth, global_eth, fx)

# Session-based storage
if "premium_log" not in st.session_state:
    st.session_state.premium_log = []

now = datetime.now().strftime("%H:%M:%S")
if premium_usdt is not None and premium_btc is not None and premium_eth is not None:
    st.session_state.premium_log.append({
        "Time": now,
        "USDT Premium": premium_usdt,
        "BTC Premium": premium_btc,
        "ETH Premium": premium_eth
    })

# Display USD/INR
st.subheader("📌 USD/INR Exchange Rate")
if fx is not None:
    st.write(f"₹{fx}")
else:
    st.warning("Failed to fetch exchange rate")

# USDT Premium
st.markdown("---")
st.subheader("💵 USDT Premium")
if p2p_usdt is not None:
    st.metric("P2P Price (INR)", f"₹{p2p_usdt}")
else:
    st.warning("Failed to fetch USDT P2P price")
st.metric("Global Price (USD)", f"${global_usdt}")
if premium_usdt is not None:
    st.metric("Premium", f"{premium_usdt}%")
else:
    st.warning("USDT premium calculation failed")

# BTC Premium
st.markdown("---")
st.subheader("🟠 BTC Premium")
if p2p_btc is not None:
    st.metric("P2P Price (INR)", f"₹{p2p_btc:,.0f}")
else:
    st.warning("Failed to fetch BTC P2P price")
if global_btc is not None:
    st.metric("Global Price (USD)", f"${global_btc:,.0f}")
else:
    st.warning("Failed to fetch BTC global price")
if premium_btc is not None:
    st.metric("Premium", f"{premium_btc}%")
else:
    st.warning("BTC premium calculation failed")

# ETH Premium
st.markdown("---")
st.subheader("🟣 ETH Premium")
if p2p_eth is not None:
    st.metric("P2P Price (INR)", f"₹{p2p_eth:,.0f}")
else:
    st.warning("Failed to fetch ETH P2P price")
if global_eth is not None:
    st.metric("Global Price (USD)", f"${global_eth:,.0f}")
else:
    st.warning("Failed to fetch ETH global price")
if premium_eth is not None:
    st.metric("Premium", f"{premium_eth}%")
else:
    st.warning("ETH premium calculation failed")

if st.session_state.premium_log:
    df = pd.DataFrame(st.session_state.premium_log)

    # Convert time column to datetime
    df["Time"] = pd.to_datetime(df["Time"])

    expected_cols = {"Time", "USDT Premium", "BTC Premium", "ETH Premium"}
    if expected_cols.issubset(set(df.columns)):
        
        # ✅ 3개 이상일 때만 그래프 출력
        if len(df) >= 3:
            st.markdown("---")
            st.subheader("📈 Real-Time Premium Trend")

            plt.figure(figsize=(10, 4))
            plt.plot(df["Time"], df["BTC Premium"], label="BTC", marker='o')
            plt.plot(df["Time"], df["ETH Premium"], label="ETH", marker='o')
            plt.plot(df["Time"], df["USDT Premium"], label="USDT", marker='o')
            plt.legend()
            plt.xticks(rotation=45)
            plt.title("Premium Trend")
            st.pyplot(plt)
        else:
            st.info(f"⏳ Waiting for more data... ({len(df)}/3 points collected)")
    else:
        st.warning("⛔ Data columns are not ready yet.")

if premium_usdt is not None and premium_btc is not None and premium_eth is not None:
    st.session_state.premium_log.append({
        "Time": now,
        "USDT Premium": premium_usdt,
        "BTC Premium": premium_btc,
        "ETH Premium": premium_eth
    })