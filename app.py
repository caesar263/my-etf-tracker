import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="源鐿科技 ETF 監控", layout="wide")
st.title("📈 每日主、被動 ETF 持股變動監控")

if os.path.exists('analysis_result.csv'):
    # 顯示變動總表
    st.subheader("📋 持股變動明細表")
    res_df = pd.read_csv('analysis_result.csv')
    st.dataframe(res_df.style.highlight_max(axis=0, subset=['增減張數']), use_container_width=True)

    # 顯示排行榜
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 買超排行榜 (張)")
        rank_df = pd.read_csv('top_ranking.csv')
        st.table(rank_df[['證券代號', '證券名稱', '增減張數']])
        
    with col2:
        st.subheader("🏗️ 產業分佈")
        st.bar_chart(data=res_df, x='產業類別', y='增減張數')
else:
    st.info("⌛ 數據更新中，請確認 GitHub Actions 已成功運行。")
