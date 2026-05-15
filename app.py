import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="源鐿科技 - 全市場 ETF 監控", layout="wide")
st.title("🏛️ 全台主動式 ETF 持股意向監控系統")

if os.path.exists('final_analysis.csv') and os.path.exists('market_ranking.csv'):
    all_data = pd.read_csv('final_analysis.csv', dtype={'股票代號': str, 'ETF代號': str})
    ranking_data = pd.read_csv('market_ranking.csv', dtype={'股票代號': str})

    # --- 第一區塊：全市場風向標 ---
    st.header("🔥 市場全域觀察：今日經理人最看好/看淡")
    col_up, col_down = st.columns(2)
    
    with col_up:
        st.subheader("📈 總加碼張數排行 (Top 5)")
        top_buy = ranking_data.sort_values(by='股數變動', ascending=False).head(5)
        top_buy['張數'] = top_buy['股數變動'] / 1000
        st.table(top_buy[['股票名稱', '張數']])

    with col_down:
        st.subheader("📉 總減碼張數排行 (Top 5)")
        top_sell = ranking_data.sort_values(by='股數變動', ascending=True).head(5)
        top_sell['張數'] = top_sell['股數變動'] / 1000
        st.table(top_sell[['股票名稱', '張數']])

    st.markdown("---")

    # --- 第二區塊：個別 ETF 查詢 ---
    st.header("🔍 個別 ETF 詳細變動")
    available_etfs = all_data['ETF代號'].unique().tolist()
    selected_etf = st.sidebar.selectbox("切換監控標的", available_etfs)
    
    df = all_data[all_data['ETF代號'] == selected_etf]
    st.subheader(f"📋 {selected_etf} 前十大持股明細")
    
    def highlight_new(val):
        return 'background-color: #fff9c4' if val == '★ 新進' else ''
    
    st.dataframe(df.style.map(highlight_new, subset=['新增偵測']), use_container_width=True)

else:
    st.warning("⌛ 14 檔 ETF 數據正在初始化中。請執行 GitHub Actions。")
