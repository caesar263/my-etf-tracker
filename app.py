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
        st.info("以下股票為今日各檔 ETF 前十大持股中「新出現」的標的：")
        st.dataframe(new_df, use_container_width=True)
    else:
        st.success("今日各檔 ETF 前十大持股名單穩定，無新進標的。")

st.divider()

# --- 區塊 2：總結與明細 ---
if os.path.exists('final_analysis.csv'):
    all_data = pd.read_csv('final_analysis.csv', dtype={'股票代號': str, 'ETF代號': str})
    
    # 顯示市場風向排行榜
    if os.path.exists('market_ranking.csv'):
        ranking = pd.read_csv('market_ranking.csv', dtype={'股票代號': str})
        if not ranking.empty and '股票名稱' in ranking.columns:
            ranking = ranking[~ranking['股票名稱'].str.contains('主動|基金|ETF', na=False)]
            
            st.header("🔥 今日經理人集體共識")
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("📈 總加碼排行榜")
                if '股數變動' in ranking.columns:
                    top_buy = ranking.sort_values(by='股數變動', ascending=False).head(5)
                    st.table(top_buy[['股票名稱', '股數變動']])
            with c2:
                st.subheader("📉 總減碼排行榜")
                if '股數變動' in ranking.columns:
                    top_sell = ranking.sort_values(by='股數變動', ascending=True).head(5)
                    st.table(top_sell[['股票名稱', '股數變動']])

    st.divider()

    st.sidebar.header("監控面板")
    etf_options = sorted(all_data['ETF代號'].unique().tolist())
    
    if etf_options:
        selected_etf = st.sidebar.selectbox("切換 ETF 標的", etf_options)
        df = all_data[all_data['ETF代號'] == selected_etf]
        
        st.subheader(f"📋 {selected_etf} {df['ETF名稱'].iloc[0]} - 前十大持股明細")
        
        # 🌟 設定正負值顏色
        def color_delta(val):
            try:
                val = float(val)
                color = 'red' if val > 0 else 'green' if val < 0 else 'black'
                return f'color: {color}'
            except:
                return 'color: black'

        # 🌟 關鍵修正：將 applymap 改為 map，解決套件版本衝突的崩潰問題
        if '權重增加比例' in df.columns:
            st.dataframe(df.style.map(color_delta, subset=['權重增加比例']), use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)
else:
    st.warning("⌛ 數據初始化中，請至 GitHub Actions 執行 Run workflow。")
