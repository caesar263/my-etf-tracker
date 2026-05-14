import streamlit as st
import pandas as pd
import os

# 網頁標題設定
st.set_page_config(page_title="源鐿科技 ETF 監控面板", layout="wide")
st.title("📊 主動式 ETF 持股變動追蹤")

# 讀取由 GitHub Actions 自動更新的數據
if os.path.exists('last_data.csv'):
    df = pd.read_csv('last_data.csv')
    
    st.subheader("今日最新持股清單")
    st.dataframe(df, use_container_width=True)
    
    # 建立簡易圖表
    st.subheader("持股權重分佈")
    st.bar_chart(data=df, x='證券名稱', y='持股比例')
else:
    st.warning("目前尚未產生數據，請先執行 GitHub Actions。")
