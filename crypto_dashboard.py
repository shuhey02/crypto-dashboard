import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 銘柄一覧
SYMBOLS = {
    "BTC/JPY": "BTC_JPY",
    "ETH/JPY": "ETH_JPY",
    "XRP/JPY": "XRP_JPY",
    "LTC/JPY": "LTC_JPY",
    "BCH/JPY": "BCH_JPY",
    "XLM/JPY": "XLM_JPY"
}

# --- データ取得（CryptoCompare）
def fetch_ohlc(symbol_code, interval="minute", limit=60):
    symbol = symbol_code.split("_")[0]
    url = f"https://min-api.cryptocompare.com/data/v2/histo{interval}"
    params = {"fsym": symbol, "tsym": "JPY", "limit": limit, "aggregate": 1}
    res = requests.get(url, params=params)
    data = res.json()["Data"]["Data"]
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df

# --- UI構成
st.set_page_config(layout="wide")
st.title("📊 仮想通貨リアルタイムダッシュボード（bitFlyer銘柄対応）")

selected_label = st.sidebar.selectbox("銘柄を選択", list(SYMBOLS.keys()))
selected_symbol = SYMBOLS[selected_label]
chart_type = st.sidebar.radio("チャート形式", ["折れ線グラフ", "ローソク足"])

df = fetch_ohlc(selected_symbol)

if chart_type == "ローソク足":
    fig = go.Figure(data=[
        go.Candlestick(x=df["time"], open=df["open"], high=df["high"],
                       low=df["low"], close=df["close"])
    ])
    fig.update_layout(title=f"{selected_label} - ローソク足", xaxis_rangeslider_visible=False)
else:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["close"], mode="lines"))
    fig.update_layout(title=f"{selected_label} - Close価格推移")

st.plotly_chart(fig, use_container_width=True)
