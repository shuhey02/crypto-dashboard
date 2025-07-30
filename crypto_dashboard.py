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

# --- 日付指定 ---
if interval_label in ["1日", "1週間", "1ヶ月"]:
    start_date = st.sidebar.date_input("開始日", value=datetime.today() - timedelta(days=7))
    end_date = st.sidebar.date_input("終了日", value=datetime.today())
    start_ts = datetime.combine(start_date, datetime.min.time())
    to_ts = datetime.combine(end_date, datetime.min.time())
else:
    selected_hour = st.sidebar.slider("表示範囲（時間）", min_value=0, max_value=12, value=12)
    to_ts = datetime.now()
    start_ts = to_ts - timedelta(hours=selected_hour)
    limit = selected_hour

show_update = st.sidebar.button("🔄 データ更新")
if show_update:
    st.experimental_rerun()

# --- グラフタイプ切替 ---
tab1, tab2 = st.tabs(["📊 高値 折れ線グラフ", "🕯️ ローソク足チャート"])

with tab1:
    st.subheader("High価格（複数銘柄）")
    fig = go.Figure()
    for symbol_label in selected_symbols:
        symbol_code = SYMBOLS[symbol_label]
        df = fetch_ohlc(symbol_code, interval=interval_code, to_ts=to_ts, limit=max_limit)
        df = df[df["time"] >= start_ts]
        if tick_format == "custom_week":
            df["time"] = df["time"].dt.to_period("W-SUN").apply(lambda p: p.start_time.strftime("%m/%d週"))
        fig.add_trace(go.Scatter(
            x=df["time"], y=df["high"],
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
        df = fetch_ohlc(symbol_code, interval=interval_code, to_ts=to_ts, limit=max_limit)
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
