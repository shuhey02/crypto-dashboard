import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 設定 ---
SYMBOLS = {
    "ビットコイン/BTC": "BTC",
    "イーサリアム/ETH": "ETH",
    "リップル/XRP": "XRP",
    "ライトコイン/LTC": "LTC",
    "ビットコインキャッシュ/BCH": "BCH",
    "ステラルーメン/XLM": "XLM",
    "カルダノ/ADA": "ADA",
    "ソラナ/SOL": "SOL",
    "ポルカドット/DOT": "DOT",
    "アバランチ/AVAX": "AVAX",
    "チェーンリンク/LINK": "LINK",
    "テゾス/XTZ": "XTZ",
    "ネム/XEM": "XEM",
    "モナコイン/MONA": "MONA",
    "メイカー/MKR": "MKR",
    "クアンタム/QTUM": "QTUM"
}

INTERVAL_MAP = {
    "1分": ("minute", 1440, "%m/%d %H:%M"),
    "1時間": ("hour", 720, "%m/%d %H:00"),
    "1日": ("day", 1095, "%Y/%m/%d"),
    "1週間": ("day", 350, "custom_week"),
    "1ヶ月": ("day", 36, "%Y/%m")
}

# --- データ取得関数（CryptoCompare） ---
def fetch_ohlc(symbol, interval="minute", to_ts=None, limit=60):
    url = f"https://min-api.cryptocompare.com/data/v2/histo{interval}"
    params = {"fsym": symbol, "tsym": "JPY", "limit": limit, "aggregate": 1}
    if to_ts:
        params["toTs"] = int(to_ts.timestamp())
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
selected_symbols = st.sidebar.multiselect("銘柄選択", list(SYMBOLS.keys()), default=["ビットコイン/BTC"], key="capsule")
interval_label = st.sidebar.selectbox("時間足", list(INTERVAL_MAP.keys()))
interval_code, max_limit, tick_format = INTERVAL_MAP[interval_label]

# --- デフォルト設定値 ---
default_offsets = {
    "1分": 60,
    "1時間": 12,
    "1日": 7,
    "1週間": 4,
    "1ヶ月": 6
}

start_offset = st.sidebar.slider("開始点 (単位に応じた前方カウント)", min_value=0, max_value=max_limit, value=default_offsets.get(interval_label, 1))
end_offset = st.sidebar.slider("終了点 (最新からのカウント)", min_value=0, max_value=max_limit, value=0)
limit = start_offset - end_offset if start_offset > end_offset else 1

if interval_label == "1日":
    start_ts = datetime.now() - timedelta(days=start_offset)
    to_ts = datetime.now() - timedelta(days=end_offset)
elif interval_label == "1週間":
    start_ts = datetime.now() - timedelta(weeks=start_offset)
    to_ts = datetime.now() - timedelta(weeks=end_offset)
elif interval_label == "1ヶ月":
    start_ts = datetime.now() - timedelta(days=30 * start_offset)
    to_ts = datetime.now() - timedelta(days=30 * end_offset)
elif interval_label == "1時間":
    start_ts = datetime.now() - timedelta(hours=start_offset)
    to_ts = datetime.now() - timedelta(hours=end_offset)
else:
    start_ts = datetime.now() - timedelta(minutes=start_offset)
    to_ts = datetime.now() - timedelta(minutes=end_offset)

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
        df = fetch_ohlc(symbol_code, interval=interval_code, to_ts=to_ts, limit=limit)
        df = df[df["time"] >= start_ts]
        if tick_format == "custom_week":
            df["time"] = df["time"].dt.to_period("W-SUN").apply(lambda p: p.start_time.strftime("%m/%d週"))
        fig.add_trace(go.Scatter(
            x=df["time"], y=df["close"],
            mode="lines",
            name=symbol_label,
            fill='tozeroy',
            fillpattern=dict(shape="/")))
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), xaxis=dict(tickformat=tick_format))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("ローソク足（複数銘柄）")
    fig = go.Figure()
    for symbol_label in selected_symbols:
        symbol_code = SYMBOLS[symbol_label]
        df = fetch_ohlc(symbol_code, interval=interval_code, to_ts=to_ts, limit=limit)
        df = df[df["time"] >= start_ts]
        if tick_format == "custom_week":
            df["time"] = df["time"].dt.to_period("W-SUN").apply(lambda p: p.start_time.strftime("%m/%d週"))
        fig.add_trace(go.Candlestick(
            x=df["time"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name=symbol_label
        ))
    fig.update_layout(xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=30, b=0), xaxis=dict(tickformat=tick_format))
    st.plotly_chart(fig, use_container_width=True)
