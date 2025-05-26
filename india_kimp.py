import streamlit as st
import requests
import time
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --------------------- 기본 설정 ---------------------
st.set_page_config(page_title="India Crypto Premium", layout="centered")
st_autorefresh(interval=60 * 1000, key="auto-refresh")

st.title("India KIMP Tracker 💹")
st.caption("실시간으로 인도 프리미엄 추이를 추적합니다.")

# --------------------- API 요청 안정화 ---------------------
def safe_get_json(url, retries=5, delay=3):
    for _ in range(retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            time.sleep(delay)
    return None

# --------------------- 가격 수집 함수들 ---------------------
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

def get_usd_inr():
    url = "https://open.er-api.com/v6/latest/USD"
    data = safe_get_json(url)
    try:
        return data["rates"]["INR"]
    except:
        return None

def calculate_premium(p2p_inr, global_usd, fx):
    if p2p_inr is not None and global_usd is not None and fx is not None:
        inr_to_usd = p2p_inr / fx
        premium = (inr_to_usd - global_usd) / global_usd * 100
        return round(premium, 2)
    return None

# --------------------- 실시간 데이터 수집 ---------------------
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

# --------------------- 세션에 프리미엄 누적 저장 ---------------------
if "premium_log" not in st.session_state:
    st.session_state.premium_log = []

now = datetime.now().strftime("%H:%M:%S")
if premium_usdt is not None and premium_btc is not None and premium_eth is not None:
    st.session_state.premium_log.append({
        "시간": now,
        "USDT 프리미엄": premium_usdt,
        "BTC 프리미엄": premium_btc,
        "ETH 프리미엄": premium_eth
    })

# --------------------- 데이터 출력 ---------------------
st.subheader("\ud83d\udcc0 USD/INR \ud655\uc728")
if fx is not None:
    st.write(f"₹{fx}")
else:
    st.warning("환율 정보를 가져오지 못했습니다.")

st.markdown("---")
st.subheader("\ud83d\udcb5 USDT 프리미엄")
if p2p_usdt is not None:
    st.metric("P2P 가격 (INR)", f"₹{p2p_usdt}")
else:
    st.warning("P2P 가격 수집 실패")
st.metric("글로벌 가격 ($)", f"${global_usdt}")
if premium_usdt is not None:
    st.metric("프리미엄", f"{premium_usdt}%")
else:
    st.warning("프리미엄 계산 실패")

st.markdown("---")
st.subheader("\ud83d\udd38 BTC 프리미엄")
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
st.subheader("\ud83d\udd39 ETH 프리미엄")
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

# --------------------- 프리미엄 변화 그래프 ---------------------
if st.session_state.premium_log:
    df = pd.DataFrame(st.session_state.premium_log)

    st.markdown("---")
    st.subheader("\ud83d\udcca \uc2e4\uc2dc\uac04 \ud504\ub9ac\ubbf8\uc5c4 \ubcc0\ud654 \ucd94\uc774")

    plt.figure(figsize=(10, 4))
    plt.plot(df["시간"], df["BTC 프리미엄"], label="BTC", marker='o')
    plt.plot(df["시간"], df["ETH 프리미엄"], label="ETH", marker='o')
    plt.plot(df["시간"], df["USDT 프리미엄"], label="USDT", marker='o')
    plt.legend()
    plt.xticks(rotation=45)
    plt.title("Premium Trend")
    plt.xlabel("time")
        st.pyplot(plt)

# --------------------- 디버깅 ---------------------
st.markdown("---")
st.subheader("\ud83d\udd27 \ub514\ubc84\uae45 \uc815\ubcf4 (\uac1c\ubc1c\uc790\uc6a9)")
st.write("환율 (fx):", fx)
st.write("BTC 글로벌 가격:", global_btc)
st.write("BTC P2P 가격:", p2p_btc)
st.write("BTC 프리미엄:", premium_btc)
st.write("ETH 글로벌 가격:", global_eth)
st.write("ETH P2P 가격:", p2p_eth)
st.write("ETH 프리미엄:", premium_eth)
