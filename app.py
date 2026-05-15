import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="主動式 ETF 前十大追蹤", layout="wide")
st.title("📊 主動式 ETF 持股每日變動分析")

if os.path.exists('final_analysis.csv'):
    df = pd.read_csv('final_analysis.csv')
    
    st.subheader("📋 前十大持股變動清單")
    
    # 樣式設定：亮黃色標註新增股票
    def highlight_new(val):
        color = 'background-color: #fff9c4' if val == '★ 新進榜' else ''
        return color

    st.dataframe(df.style.applymap(highlight_new, subset=['新增偵測']), use_container_width=True)
    
    # 圖表呈現
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 股數增減 (張)")
        df['張數變動'] = df['股數變動'] / 1000
        st.bar_chart(data=df, x='股票名稱', y='張數變動')
    with col2:
        st.subheader("⚖️ 權重位移 (%)")
        st.bar_chart(data=df, x='股票名稱', y='權重變動')
else:
    st.warning("尚未偵測到數據，請先至 GitHub Actions 手動點擊 Run workflow。")
