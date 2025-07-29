import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# --- 対応銘柄リスト（bitFlyer銘柄）
SYMBOLS = {
    "BTC/JPY": "BTC",
    "ETH/JPY": "ETH",
    "XRP/JPY": "XRP",
    "LTC/JPY": "LTC",
    "BCH/JPY": "BCH",
    "XLM/JPY": "XLM"
}

# --- 時間足変換表（CryptoCompare APIに準拠）
INTERVAL_MAP = {
    "1分足": ("minute", 60),
    "1時間足": ("hour", 24),
    "日足": ("day", 30)
}

# --- データ取得関数（CryptoCompare）
def fetch_ohlc(symbol, interval="minute", limit=60):
    url = f"https://min-api.cryptocompare.com/data/v2/histo{interval}"
    params = {"fsym": symbol, "tsym": "JPY", "limit": limit, "aggregate": 1}
    res = requests.get(url, params=params)
    data = res.json()["Data"]["Data"]
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df

# --- UI構成 ---
st.set_page_config(layout="wide")
st.title("📈 仮想通貨ダッシュボード（複数銘柄・時間軸・タブ対応）")

# --- サイドバー操作 ---
selected_symbols = st.sidebar.multiselect("表示する銘柄（複数選択可）", list(SYMBOLS.keys()), default=["BTC/JPY"])
interval_label = st.sidebar.selectbox("時間足を選択", list(INTERVAL_MAP.keys()))
show_update = st.sidebar.button("🔄 データを更新")

# --- データ再読み込み（更新ボタン用） ---
if show_update:
    st.experimental_rerun()

interval_code, limit = INTERVAL_MAP[interval_label]

# --- グラフタブ表示 ---
tab1, tab2 = st.tabs(["📊 折れ線グラフ", "🕯️ ローソク足チャート"])

# --- 複数銘柄ループ ---
for symbol_label in selected_symbols:
    symbol_code = SYMBOLS[symbol_label]
    df = fetch_ohlc(symbol_code, interval=interval_code, limit=limit)

    with tab1:
        st.subheader(f"{symbol_label} - {interval_label} (Close価格)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["time"], y=df["close"], mode="lines", name="Close"))
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader(f"{symbol_label} - {interval_label}（ローソク足）")
        candle = go.Figure(data=[
            go.Candlestick(
                x=df["time"],
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"]
            )
        ])
        candle.update_layout(xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(candle, use_container_width=True)
