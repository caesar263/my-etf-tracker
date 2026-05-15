import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="源鐿科技 - 全市場監控", layout="wide")
st.title("🏛️ 全台主動式 ETF 持股意向監控系統")

# 內建名稱對照表，防止 CSV 缺漏欄位導致崩潰
etf_names_map = {
    "00981A": "統一台股增長", "00994A": "第一金台股優選", "00992A": "群益科技創新",
    "00987A": "台新優勢成長", "00995A": "中信台灣卓越", "00991A": "復華未來50",
    "00985A": "野村台灣50", "00982A": "群益台灣強棒", "00980A": "野村臺灣優選",
    "00984A": "安聯台灣高息成長", "00996A": "兆豐台灣豐收", "00400A": "國泰動能高息",
    "00993A": "安聯台灣", "00401A": "摩根台灣鑫收", "00403A": "統一升級50"
}

if os.path.exists('final_analysis.csv'):
    all_data = pd.read_csv('final_analysis.csv', dtype={'股票代號': str, 'ETF代號': str})
    
    if os.path.exists('market_ranking.csv'):
        ranking = pd.read_csv('market_ranking.csv', dtype={'股票代號': str})
        
        # 🌟 自動過濾掉誤抓成股票的 ETF 基金名稱
        ranking = ranking[~ranking['股票名稱'].str.contains('主動|基金|ETF', na=False)]
        
        st.header("🔥 今日經理人集體共識")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📈 總加碼排行榜")
            top_buy = ranking.sort_values(by='股數變動', ascending=False).head(5)
            st.table(top_buy[['股票名稱', '股數變動']])
        with c2:
            st.subheader("📉 總減碼排行榜")
            top_sell = ranking.sort_values(by='股數變動', ascending=True).head(5)
            st.table(top_sell[['股票名稱', '股數變動']])

    st.divider()

    st.sidebar.header("監控面板")
    etf_options = sorted(all_data['ETF代號'].unique().tolist())
    selected_etf = st.sidebar.selectbox("切換 ETF 標的", etf_options)
    
    # 安全取得名稱
    fund_name = etf_names_map.get(selected_etf, "")
    df = all_data[all_data['ETF代號'] == selected_etf]
    
    st.subheader(f"📋 {selected_etf} {fund_name} - 前十大持股明細")
    
    def highlight_new(val):
        return 'background-color: #fff9c4' if val == '★ 新進' else ''
    
    if '新增偵測' in df.columns:
        st.dataframe(df.style.map(highlight_new, subset=['新增偵測']), use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)
else:
    st.warning("⌛ 數據初始化中，請至 GitHub Actions 執行 Run workflow。")
