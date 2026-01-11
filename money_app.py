import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests
from datetime import datetime

# --- 1. 初始化設定 ---
st.set_page_config(page_title="雲端雙幣帳本", layout="wide")

# 2. 強制宣告網頁語系為繁體中文 (防止瀏覽器跳出翻譯視窗)
st.markdown(
    """
    <script>
        document.documentElement.lang = 'zh-Hant';
    </script>
    """,
    unsafe_allow_html=True
)

# 設定你的試算表網址 (請填入你剛剛複製的網址)
url = "https://docs.google.com/spreadsheets/d/1KH7DE51xdd6ld5ThFsow8tIDX9_bBqbSoSPdcR4UeAM/edit?usp=sharing"

# 建立 Google Sheets 連線
conn = st.connection("gsheets", type=GSheetsConnection)

# 讀取現有雲端資料
# 如果是第一次使用，會因為沒資料報錯，所以我們加一個 try-except
try:
    df = conn.read(spreadsheet=url, usecols=[0,1,2,3,4,5,6])
    df = df.dropna(how="all") # 移除空白列
except:
    df = pd.DataFrame(columns=["旅程名稱", "日期", "類別", "項目", "幣別", "原始金額", "台幣總計"])

# 匯率抓取
@st.cache_data(ttl=3600)
def get_exchange_rate():
    try:
        response = requests.get("https://open.er-api.com/v6/latest/JPY")
        return response.json()['rates']['TWD']
    except:
        return 0.21
rate = get_exchange_rate()

# --- 2. 介面設計 ---
st.title("☁️ 雲端同步預算管家")

# 旅程選擇
st.sidebar.title("🧳 旅程管理")
existing_trips = df["旅程名稱"].unique().tolist() if not df.empty else []
all_options = existing_trips + ["+ 建立新旅程"]
selected_option = st.sidebar.selectbox("切換當前旅程", all_options)

if selected_option == "+ 建立新旅程":
    current_trip = st.sidebar.text_input("輸入新旅程名稱")
else:
    current_trip = selected_option

# --- 3. 新增紀錄邏輯 ---
with st.expander("➕ 新增支出", expanded=True):
    c1, c2, c3 = st.columns(3)
    item = c1.text_input("項目")
    category = c1.selectbox("類別", ["飲食", "交通", "住宿", "滑雪", "購物"])
    currency = c2.radio("幣別", ["JPY", "TWD"])
    amount = c2.number_input("金額", min_value=0.0)
    date = c3.date_input("日期", datetime.now())

    if st.button("同步到雲端", use_container_width=True):
        if item and amount > 0 and current_trip:
            twd_total = amount * rate if currency == "JPY" else amount
            new_row = pd.DataFrame([[current_trip, str(date), category, item, currency, amount, twd_total]], columns=df.columns)
            
            # 合併舊資料與新資料
            updated_df = pd.concat([df, new_row], ignore_index=True)
            
            # 寫入雲端 Google Sheets
            conn.update(spreadsheet=url, data=updated_df)
            
            st.success("✅ 資料已同步到 Google 試算表！")
            st.balloons()
            st.rerun()

# --- 4. 顯示統計 ---
if not df.empty and current_trip:
    trip_df = df[df["旅程名稱"] == current_trip]
    if not trip_df.empty:
        st.subheader(f"📊 {current_trip} 支出明細")
        st.dataframe(trip_df, use_container_width=True)
        st.metric("總支出 (TWD)", f"NT$ {trip_df['台幣總計'].sum():,.0f}")

