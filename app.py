import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="主動式 ETF 前十大監控", layout="wide")
st.title("🔎 主動式 ETF 前十大持股每日變動")

if os.path.exists('analysis_result.csv'):
    df = pd.read_csv('analysis_result.csv')
    st.subheader("📋 前 10 大持股明細變動")
    
    # 標註新增股票顏色
    def highlight_new(row):
        return ['background-color: #e6f3ff' if row['新增狀態'] == '✨ 新進榜' else '' for _ in row]
    
    st.dataframe(df.style.apply(highlight_new, axis=1), use_container_width=True)
    
    st.subheader("📊 權重變動趨勢")
    if '權重變動' in df.columns:
        st.bar_chart(data=df, x='股票名稱', y='權重變動')
else:
    st.info("⌛ 數據初始化中，請手動點擊 GitHub Actions 執行第一次抓取。")
