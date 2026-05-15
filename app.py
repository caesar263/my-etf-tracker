import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="源鐿科技 - ETF 監控", layout="wide")
st.title("🏛️ 全台主動式 ETF 持股意向監控系統")

# --- 區塊 1：今日新進榜股票總覽 ---
if os.path.exists('new_additions.csv'):
    new_df = pd.read_csv('new_additions.csv', dtype={'ETF代號': str})
    if not new_df.empty:
        st.header("✨ 今日新進榜股票總覽")
        # 🌟 這裡會顯示新增股票在該 ETF 的權重增加比例
        st.dataframe(new_df, use_container_width=True)

st.divider()

# --- 區塊 2：總結與明細 (同樣會包含權重變動) ---
if os.path.exists('final_analysis.csv'):
    all_data = pd.read_csv('final_analysis.csv', dtype={'股票代號': str, 'ETF代號': str})
    
    st.sidebar.header("監控面板")
    selected_etf = st.sidebar.selectbox("切換 ETF 標的", sorted(all_data['ETF代號'].unique().tolist()))
    
    df = all_data[all_data['ETF代號'] == selected_etf]
    st.subheader(f"📋 {selected_etf} {df['ETF名稱'].iloc[0]} - 前十大持股明細")
    
    # 🌟 透過樣式醒目顯示權重增加的部分
    def color_delta(val):
        color = 'red' if val > 0 else 'green' if val < 0 else 'black'
        return f'color: {color}'

    st.dataframe(df.style.applymap(color_delta, subset=['權重增加比例']), use_container_width=True)
