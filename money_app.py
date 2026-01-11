import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="旅遊雙幣帳本", layout="wide")

# --- 1. 抓取即時匯率 (日幣轉台幣) ---
@st.cache_data(ttl=3600) # 每小時更新一次，避免過度讀取
def get_exchange_rate():
    try:
        # 使用公開 API 抓取日圓對台幣匯率
        response = requests.get("https://open.er-api.com/v6/latest/JPY")
        data = response.json()
        return data['rates']['TWD']
    except:
        return 0.21 # 報錯時的保底匯率

rate = get_exchange_rate()

st.title("❄️ 2026日本旅遊收支紀錄")
st.sidebar.info(f"📅 當前 JPY/TWD 匯率：{rate:.4f}")

# --- 2. 輸入介面 ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        item = st.text_input("項目名稱")
        category = st.selectbox("類別", ["飲食", "交通", "滑雪", "購物", "其他"])
    with col2:
        currency = st.radio("幣別", ["日幣 (JPY)", "台幣 (TWD)"], horizontal=True)
        amount = st.number_input("輸入金額", min_value=0.0)

# --- 3. 邏輯處理 ---
if st.button("確認記錄", use_container_width=True):
    if item and amount > 0:
        # 計算轉換後的金額
        jpy_val = amount if currency == "日幣 (JPY)" else amount / rate
        twd_val = amount * rate if currency == "日幣 (JPY)" else amount
        
        # 這裡示範顯示結果，下一階段我們可以教你存入資料庫
        st.success(f"✅ 已記錄：{item}")
        st.metric("日幣總計", f"¥ {jpy_val:,.0f}")
        st.metric("台幣總計 (即時匯率)", f"NT$ {twd_val:,.0f}")
        st.balloons()
    else:
        st.warning("請填寫項目與金額")

st.divider()
st.caption("提示：手機版建議將此網頁「加入主畫面」以當作 APP 使用。")