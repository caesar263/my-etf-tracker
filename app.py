import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="ETF 前十大變動監控", layout="wide")
st.title("📊 主動式 ETF 持股每日變動分析")

# 檢查分析結果檔案是否存在
if os.path.exists('final_analysis.csv'):
    df = pd.read_csv('final_analysis.csv')
    
    st.subheader("📋 前十大持股變動清單")
    
    # 修正：使用 map 取代已過時的 applymap
    def highlight_new(val):
        if val == '★ 新進榜':
            return 'background-color: #fff9c4' # 亮黃色
        return ''

    # 確保『新增偵測』欄位存在才進行標註
    if '新增偵測' in df.columns:
        styled_df = df.style.map(highlight_new, subset=['新增偵測'])
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)
    
    # 圖表呈現
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
    st.warning("🚀 數據正在初始化。請至 GitHub Actions 手動執行一次 Run workflow，明天即可看到變動對比。")
