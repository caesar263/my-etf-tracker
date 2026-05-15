import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="ETF 持股監控", layout="wide")
st.title("📊 主動式 ETF 前十大持股每日變動")

if os.path.exists('final_analysis.csv'):
    df = pd.read_csv('final_analysis.csv')
    
    st.subheader("📋 前十大持股變動清單")
    
    # 使用通用的 style 函數，避免套件版本衝突
    def color_new(val):
        color = 'background-color: #fff9c4' if val == '★ 新進榜' else ''
        return color

    if '新增偵測' in df.columns:
        # 使用最新的建議語法
        st.dataframe(df.style.applymap(color_new, subset=['新增偵測']), use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)
    
    # 變動圖表
    col1, col2 = st.columns(2)
    with col1:
        if '股數變動' in df.columns:
            st.subheader("📈 股數增減 (張)")
            df['張數變動'] = df['股數變動'] / 1000
            st.bar_chart(data=df, x='股票名稱', y='張數變動')
    with col2:
        if '權重變動' in df.columns:
            st.subheader("⚖️ 權重變動 (%)")
            st.bar_chart(data=df, x='股票名稱', y='權重變動')
else:
    st.warning("🚀 數據正在路上！請至 GitHub Actions 點擊 Run workflow，完成後重新整理網頁即可。")
