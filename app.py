import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="ETF 前十大變動監控", layout="wide")
st.title("📊 主動式 ETF 前十大持股每日變動分析")

if os.path.exists('final_analysis.csv'):
    # 讀取時同樣強制指定代號為字串
    df = pd.read_csv('final_analysis.csv', dtype={'股票代號': str})
    
    st.subheader("📋 前十大持股變動清單")
    
    def highlight_new(val):
        return 'background-color: #fff9c4' if val == '★ 新進榜' else ''

    if '新增偵測' in df.columns:
        # 使用 map 確保相容性
        styled_df = df.style.map(highlight_new, subset=['新增偵測'])
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if '股數變動' in df.columns:
            st.subheader("📈 股數增減 (張)")
            df['張數變動'] = df['股數變動'] / 1000
            st.bar_chart(data=df, x='股票名稱', y='張數變動')
    with col2:
        if '權重變動' in df.columns:
            st.subheader("⚖️ 權重位移 (%)")
            st.bar_chart(data=df, x='股票名稱', y='權重變動')
else:
    st.warning("⌛ 數據初始化中。請至 GitHub Actions 手動點擊 Run workflow。")
