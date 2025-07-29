import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

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
    "1分足": ("minute", 1440),      # 最大1440件（1日）
    "1時間足": ("hour", 720),       # 最大720件（30日）
    "日足": ("day", 365)            # 最大365件（1年）
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

# --- 移動平均の計算 ---
def add_moving_averages(df):
    df["MA_5"] = df["close"].rolling(window=5).mean()
    df["MA_20"] = df["close"].rolling(window=20).mean()
    return df

# --- UI ---
st.set_page_config(layout="wide")
st.markdown("""
    <h1 style='color:#00ffff'>📈 仮想通貨ダッシュボード</h1>
    <p style='color:gray;'>複数銘柄・期間・インジケーター・ダークモード対応</p>
    <hr>
""", unsafe_allow_html=True)

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
    st.subheader("Close価格 & 移動平均線（複数銘柄）")
    fig = go.Figure()
    for symbol_label in selected_symbols:
        symbol_code = SYMBOLS[symbol_label]
        df = fetch_ohlc(symbol_code, interval=interval_code, limit=limit)
        df = add_moving_averages(df)
        fig.add_trace(go.Scatter(x=df["time"], y=df["close"], mode="lines", name=f"{symbol_label} - Close"))
        fig.add_trace(go.Scatter(x=df["time"], y=df["MA_5"], mode="lines", name=f"{symbol_label} - MA5", line=dict(dash='dot')))
        fig.add_trace(go.Scatter(x=df["time"], y=df["MA_20"], mode="lines", name=f"{symbol_label} - MA20", line=dict(dash='dash')))
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    for symbol_label in selected_symbols:
        symbol_code = SYMBOLS[symbol_label]
        df = fetch_ohlc(symbol_code, interval=interval_code, limit=limit)
        df = add_moving_averages(df)
        st.subheader(f"{symbol_label} - ローソク足 + 出来高 + 移動平均")
        candle = go.Figure()
        candle.add_trace(go.Candlestick(x=df["time"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="OHLC"))
        candle.add_trace(go.Scatter(x=df["time"], y=df["MA_5"], mode="lines", name="MA5", line=dict(dash='dot')))
        candle.add_trace(go.Scatter(x=df["time"], y=df["MA_20"], mode="lines", name="MA20", line=dict(dash='dash')))
        candle.add_trace(go.Bar(x=df["time"], y=df["volumefrom"], name="出来高", marker=dict(color="gray"), yaxis='y2'))
        candle.update_layout(
            xaxis_rangeslider_visible=False,
            template="plotly_dark",
            yaxis=dict(title="価格"),
            yaxis2=dict(title="出来高", overlaying='y', side='right', showgrid=False)
        )
        st.plotly_chart(candle, use_container_width=True)

        # --- 統計表示 ---
        st.info(f"最大価格: {df['high'].max():,.0f} / 最小価格: {df['low'].min():,.0f} / 平均: {df['close'].mean():,.0f}")
