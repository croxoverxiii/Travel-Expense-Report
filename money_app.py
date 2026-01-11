import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime

# --- 1. 初始化與設定 ---
st.set_page_config(page_title="滑雪雙幣帳本", layout="wide")

# 匯率抓取功能
@st.cache_data(ttl=3600)
def get_exchange_rate():
    try:
        response = requests.get("https://open.er-api.com/v6/latest/JPY")
        return response.json()['rates']['TWD']
    except:
        return 0.21

rate = get_exchange_rate()

# --- 2. 旅程管理邏輯 ---
# 這裡我們用一個 CSV 檔案存所有人的資料
DB_FILE = "all_trips_data.csv"
if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
else:
    df = pd.DataFrame(columns=["旅程名稱", "日期", "類別", "項目", "幣別", "原始金額", "台幣總計"])

# --- 3. 側邊欄：旅程切換 ---
st.sidebar.title("🧳 旅程管理")
existing_trips = df["旅程名稱"].unique().tolist() if not df.empty else []
all_options = existing_trips + ["+ 建立新旅程"]
selected_option = st.sidebar.selectbox("切換當前旅程", all_options)

if selected_option == "+ 建立新旅程":
    current_trip = st.sidebar.text_input("輸入新旅程名稱 (如: 2026東京)")
else:
    current_trip = selected_option

st.sidebar.divider()
st.sidebar.info(f"💡 目前匯率: 1 JPY = {rate:.4f} TWD")

# --- 4. 主介面：輸入區 ---
st.title(f"❄️ {current_trip if current_trip else '請先命名旅程'}")

with st.expander("➕ 新增一筆支出", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        item = st.text_input("項目")
        category = st.selectbox("類別", ["飲食", "交通", "住宿", "滑雪", "購物"])
    with col2:
        currency = st.radio("幣別", ["JPY", "TWD"])
        amount = st.number_input("金額", min_value=0.0)
    with col3:
        date = st.date_input("日期", datetime.now())

    if st.button("確認記錄", use_container_width=True):
        if item and amount > 0 and current_trip:
            # 計算台幣金額
            twd_total = amount * rate if currency == "JPY" else amount
            
            # 存入 DataFrame
            new_row = pd.DataFrame([[current_trip, date, category, item, currency, amount, twd_total]], columns=df.columns)
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.success(f"已存入 {current_trip}！")
            st.balloons()
            st.rerun()

# --- 5. 數據顯示 ---
st.divider()
if not df.empty and current_trip:
    # 只顯示當前旅程的資料
    trip_df = df[df["旅程名稱"] == current_trip]
    
    if not trip_df.empty:
        st.subheader(f"📊 {current_trip} 支出明細")
        st.dataframe(trip_df, use_container_width=True)
        
        total = trip_df["台幣總計"].sum()
        st.metric("當前旅程總支出", f"NT$ {total:,.0f}")
    else:
        st.info("這個旅程還沒有資料喔！")
