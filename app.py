import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="源鐿科技 - 多檔 ETF 監控", layout="wide")
st.title("📊 多檔主動式 ETF 同時監控系統")

if os.path.exists('final_analysis.csv'):
    # 強制代號為字串，確保與 CSV 一致
    all_data = pd.read_csv('final_analysis.csv', dtype={'股票代號': str, 'ETF代號': str})
    
    # 側邊欄選擇器
    st.sidebar.header("監控設定")
    available_etfs = all_data['ETF代號'].unique().tolist()
    selected_etf = st.sidebar.selectbox("請選擇要查看的 ETF", available_etfs)
    
    # 篩選資料
    df = all_data[all_data['ETF代號'] == selected_etf]
    
    st.subheader(f"📋 {selected_etf} 前十大持股變動清單")
    
    def highlight_new(val):
        return 'background-color: #fff9c4' if val == '★ 新進榜' else ''

    styled_df = df.style.map(highlight_new, subset=['新增偵測'])
    st.dataframe(styled_df, use_container_width=True)
    
    # 視覺化
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 股數增減 (張)")
        df['張數變動'] = df['股數變動'] / 1000
        st.bar_chart(data=df, x='股票名稱', y='張數變動')
    with col2:
        st.subheader("⚖️ 權重變動 (%)")
        st.bar_chart(data=df, x='股票名稱', y='權重變動')
else:
    st.warning("⌛ 多檔數據正在初始化中。請執行 GitHub Actions。")
