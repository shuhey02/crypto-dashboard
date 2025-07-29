import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 設定 ---
SYMBOLS = {
    "BTC/JPY": "BTC",
    "ETH/JPY": "ETH",
    "XRP/JPY": "XRP",
    "LTC/JPY": "LTC",
    "BCH/JPY": "BCH",
    "XLM/JPY": "XLM"
}

INTERVAL_MAP = {
    "1分足": ("minute", 2000),      # 最大2000件（約33時間）
    "1時間足": ("hour", 2000),       # 最大2000件（約83日）
    "日足": ("day", 2000)            # 最大2000件（約5年）
}

# --- データ取得関数（CryptoCompare） ---
def fetch_ohlc(symbol, interval="minute", limit=60):
    url = f"https://min-api.cryptocompare.com/data/v2/histo{interval}"
    params = {"fsym": symbol, "tsym": "JPY", "limit": limit, "aggregate": 1}
    res = requests.get(url, params=params)
    data = res.json()["Data"]["Data"]
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df

# --- UI ---
st.set_page_config(layout="wide")
st.title("📈 仮想通貨ダッシュボード")

# --- サイドバー ---
st.sidebar.header("表示設定")
selected_symbols = st.sidebar.multiselect("銘柄選択", list(SYMBOLS.keys()), default=["BTC/JPY"], key="capsule")
interval_label = st.sidebar.selectbox("時間足", list(INTERVAL_MAP.keys()))
interval_code, max_limit = INTERVAL_MAP[interval_label]
limit = st.sidebar.slider("表示本数（期間）", min_value=30, max_value=max_limit, value=100)
show_update = st.sidebar.button("🔄 データ更新")

if show_update:
    st.experimental_rerun()

# --- グラフタイプ切替 ---
tab1, tab2 = st.tabs(["📊 折れ線グラフ", "🕯️ ローソク足チャート"])

with tab1:
    st.subheader("Close価格（複数銘柄）")
    fig = go.Figure()
    for symbol_label in selected_symbols:
        symbol_code = SYMBOLS[symbol_label]
        df = fetch_ohlc(symbol_code, interval=interval_code, limit=limit)
        fig.add_trace(go.Scatter(x=df["time"], y=df["close"], mode="lines", name=symbol_label))
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), xaxis=dict(tickformat="%m/%d"))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("ローソク足（複数銘柄）")
    fig = go.Figure()
    for symbol_label in selected_symbols:
        symbol_code = SYMBOLS[symbol_label]
        df = fetch_ohlc(symbol_code, interval=interval_code, limit=limit)
        fig.add_trace(go.Candlestick(
            x=df["time"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name=symbol_label
        ))
    fig.update_layout(xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=30, b=0), xaxis=dict(tickformat="%m/%d"))
    st.plotly_chart(fig, use_container_width=True)
