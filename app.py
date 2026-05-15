import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="源鐿科技 - 全市場監控", layout="wide")
st.title("🏛️ 全台 14 檔主動式 ETF 持股意向監控")

if os.path.exists('final_analysis.csv'):
    all_data = pd.read_csv('final_analysis.csv', dtype={'股票代號': str, 'ETF代號': str})
    
    # --- 第一部分：市場風向標 ---
    if os.path.exists('market_ranking.csv'):
        ranking = pd.read_csv('market_ranking.csv', dtype={'股票代號': str})
        st.header("🔥 今日經理人集體共識")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📈 總加碼排行榜")
            st.table(ranking.sort_values(by='股數變動', ascending=False).head(5)[['股票名稱', '股數變動']])
        with c2:
            st.subheader("📉 總減碼排行榜")
            st.table(ranking.sort_values(by='股數變動', ascending=True).head(5)[['股票名稱', '股數變動']])

    st.divider()

    # --- 第二部分：個別 ETF 查詢 ---
    st.sidebar.header("監控面板")
    etf_options = sorted(all_data['ETF代號'].unique().tolist())
    selected_etf = st.sidebar.selectbox("切換 ETF 標的", etf_options)
    
    fund_name = all_data[all_data['ETF代號'] == selected_etf]['ETF名稱'].iloc[0]
    df = all_data[all_data['ETF代號'] == selected_etf]
    
    st.subheader(f"📋 {selected_etf} {fund_name} - 前十大持股明細")
    st.dataframe(df, use_container_width=True)
else:
    st.info("⌛ 數據獲取中，請在 GitHub Actions 執行 Run workflow。")
