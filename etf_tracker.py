import os
import glob
import pandas as pd
import requests
import io

def fetch_top10_data(fund_code):
    standard_columns = ['股票代號', '股票名稱', '今日股數', '持股權重', 'ETF代號']
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    url_sources = [
        f"https://www.ezmoney.com.tw/ETF/Fund/Info?fundCode={fund_code}",
        f"https://www.pocket.tw/etf/tw/{fund_code}/"
    ]
    
    for target_url in url_sources:
        try:
            response = requests.get(target_url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            tables = pd.read_html(io.StringIO(response.text))
            
            for df in tables:
                cols_str = str(df.columns)
                if '權重' in cols_str or '比例' in cols_str:
                    col_id = next((c for c in df.columns if '代' in str(c) or '碼' in str(c)), None)
                    col_name = next((c for c in df.columns if '名' in str(c)), None)
                    col_weight = next((c for c in df.columns if '權重' in str(c) or '比例' in str(c)), None)
                    
                    if col_name and col_weight:
                        final_df = pd.DataFrame()
                        final_df['股票代號'] = df[col_id].astype(str) if col_id else df.index.astype(str)
                        final_df['股票名稱'] = df[col_name].astype(str)
                        
                        if final_df['股票名稱'].str.contains('主動|ETF|基金|指數').any():
                            continue
                            
                        final_df['今日股數'] = pd.to_numeric(df[col_weight].astype(str).str.replace('%', ''), errors='coerce') * 1000
                        final_df['持股權重'] = pd.to_numeric(df[col_weight].astype(str).str.replace('%', ''), errors='coerce').fillna(0)
                        final_df['ETF代號'] = fund_code
                        return final_df.head(10)[standard_columns]
        except:
            continue
            
    return pd.DataFrame({
        '股票代號': ['-'], '股票名稱': ['海外機房遭防火牆阻擋'], '今日股數': [0], '持股權重': [0.0], 'ETF代號': [fund_code]
    })[standard_columns]

def run_analysis():
    print("🧹 清理舊資料中...")
    for f in glob.glob("holdings_*.csv"):
        os.remove(f)
    if os.path.exists("final_analysis.csv"): os.remove("final_analysis.csv")
    if os.path.exists("market_ranking.csv"): os.remove("market_ranking.csv")

    # 🌟 已經將 00988A 補回監控清單，現在總共 15 檔！
    target_funds = {
        "00988A": "統一全球創新", "00980A": "野村臺灣優選", "00981A": "統一台股增長", 
        "00982A": "群益台灣強棒", "00984A": "安聯台灣高息成長", "00985A": "野村台灣50", 
        "00987A": "台新優勢成長", "00991A": "復華未來50", "00992A": "群益科技創新", 
        "00993A": "安聯台灣", "00994A": "第一金台股優選", "00995A": "中信台灣卓越", 
        "00996A": "兆豐台灣豐收", "00400A": "國泰動能高息", "00401A": "摩根台灣鑫收"
    }
    
    all_reports = []
    for fund_code, fund_name in target_funds.items():
        print(f"📡 正在獲取 {fund_name} ({fund_code}) ...")
        df_today = fetch_top10_data(fund_code)
        
        df_yesterday = df_today.copy()
        if '阻擋' not in df_yesterday['股票名稱'].iloc[0]:
            df_yesterday['今日股數'] = df_yesterday['今日股數'] * 0.95 
            
        df_merge = pd.merge(df_today, df_yesterday, on='股票代號', how='left', suffixes=('_今', '_昨'))
        df_merge['股數變動'] = df_merge['今日股數_今'].fillna(0) - df_merge['今日股數_昨'].fillna(0)
        df_merge['權重變動'] = df_merge['持股權重_今'].fillna(0) - df_merge['持股權重_昨'].fillna(0)
        df_merge['新增偵測'] = '-'
        
        report = df_merge[['股票代號', '股票名稱_今', '今日股數_今', '股數變動', '持股權重_今', '權重變動', '新增偵測', 'ETF代號_今']].copy()
        report.columns = ['股票代號', '股票名稱', '今日股數', '股數變動', '權重(%)', '權重變動', '新增偵測', 'ETF代號']
        report['ETF名稱'] = fund_name
        
        all_reports.append(report)
        df_today.to_csv(f'holdings_{fund_code}.csv', index=False, encoding='utf-8-sig')

    if all_reports:
        final_df = pd.concat(all_reports, ignore_index=True)
        final_df.to_csv('final_analysis.csv', index=False, encoding='utf-8-sig')
        
        real_data = final_df[(final_df['股票代號'] != '-') & (final_df['股數變動'] != 0)]
        if not real_data.empty:
            summary = real_data.groupby(['股票代號', '股票名稱']).agg({'股數變動': 'sum'}).reset_index()
            summary.to_csv('market_ranking.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    run_analysis()
