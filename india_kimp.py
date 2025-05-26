import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

# ✅ 가장 먼저 호출해야 함
st.set_page_config(page_title="India Crypto Premium", layout="centered")
st_autorefresh(interval=60 * 1000, key="auto-refresh")

st.title("🇮🇳 인도 코인 프리미엄 실시간 트래커")
st.caption("⏱️ 60초마다 자동 갱신됩니다.")

# ✅ P2P 가격 수집 함수
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

# ✅ CoinGecko를 통한 글로벌 시세 수집 함수
def get_global_price_usdt(symbol):
    symbol_map = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "USDT": "tether"
    }
    if symbol not in symbol_map:
        return None
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol_map[symbol]}&vs_currencies=usd"
        response = requests.get(url).json()
        return float(response[symbol_map[symbol]]["usd"])
    except:
        return None

# ✅ 환율 수집 함수
def get_usd_inr():
    try:
        url = "https://api.frankfurter.app/latest?from=USD&to=INR"
        return requests.get(url).json()['rates']['INR']
    except:
        return None

# ✅ 프리미엄 계산 함수
def calculate_premium(p2p_inr, global_usd, fx):
    if p2p_inr is not None and global_usd is not None and fx is not None:
        inr_to_usd = p2p_inr / fx
        premium = (inr_to_usd - global_usd) / global_usd * 100
        return round(premium, 2)
    return None

# ✅ 데이터 수집
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

# ✅ 화면 출력
st.subheader("📌 USD/INR 환율")
if fx is not None:
    st.write(f"₹{fx}")
else:
    st.warning("환율 정보를 가져오지 못했습니다.")

st.markdown("---")
st.subheader("💵 USDT 프리미엄")
if p2p_usdt is not None:
    st.metric("P2P 가격 (INR)", f"₹{p2p_usdt}")
else:
    st.warning("P2P 가격 수집 실패")

st.metric("글로벌 가격 ($)", f"${global_usdt}")  # USDT는 고정
if premium_usdt is not None:
    st.metric("프리미엄", f"{premium_usdt}%")
else:
    st.warning("프리미엄 계산 실패")

st.markdown("---")
st.subheader("🟠 BTC 프리미엄")
if p2p_btc is not None:
    st.metric("P2P 가격 (INR)", f"₹{p2p_btc:,.0f}")
else:
    st.warning("P2P 가격 수집 실패")

if global_btc is not None:
    st.metric("글로벌 가격 ($)", f"${global_btc:,.0f}")
else:
    st.warning("글로벌 시세 수집 실패")

if premium_btc is not None:
    st.metric("프리미엄", f"{premium_btc}%")
else:
    st.warning("프리미엄 계산 실패")

st.markdown("---")
st.subheader("🟣 ETH 프리미엄")
if p2p_eth is not None:
    st.metric("P2P 가격 (INR)", f"₹{p2p_eth:,.0f}")
else:
    st.warning("P2P 가격 수집 실패")

if global_eth is not None:
    st.metric("글로벌 가격 ($)", f"${global_eth:,.0f}")
else:
    st.warning("글로벌 시세 수집 실패")

if premium_eth is not None:
    st.metric("프리미엄", f"{premium_eth}%")
else:
    st.warning("프리미엄 계산 실패")
