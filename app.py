import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="主動式 ETF 前十大監控", layout="wide")

st.title("🔎 主動式 ETF 前十大持股每日變動監控")

if os.path.exists('display_result.csv'):
    df = pd.read_csv('display_result.csv')
    
    # 顯示前十大股票變動
    st.subheader("📋 每日變動清單 (前 10 大股票)")
    
    # 使用表格樣式，將新增股票特別標註顏色
    def highlight_new(val):
        color = 'background-color: #ffffcc' if val == '✨ 新增' else ''
        return color

    st.dataframe(df.style.applymap(highlight_new, subset=['新增狀態']), use_container_width=True)
    
    # 權重變動視覺化
    if '每日權重變動' in df.columns:
        st.subheader("📊 前十大權重增減趨勢")
        st.bar_chart(data=df, x='股票名稱', y='每日權重變動')
else:
    st.info("⌛ 目前尚無對比數據。請點擊 GitHub Actions 執行第一次抓取，明天即可看到變動。")
