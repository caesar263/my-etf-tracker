import os
import glob
import pandas as pd
import requests
import io

# 標準化名稱字典 (持續維護)
STANDARD_NAMES = {
    "2330": "台積電", "2317": "鴻海", "2454": "聯發科", "6669": "緯穎",
    "3231": "緯創", "2382": "廣達", "2308": "台達電", "2881": "富邦金",
    "3711": "日月光投控", "3017": "奇鋐", "6274": "台燿", "6187": "萬潤"
}

def standardize_stock(row):
    code = str(row['股票代號']).strip()
    name = str(row['股票名稱']).strip().upper()
    if len(code) < 3 or not code.isdigit():
        if '台積' in name: code = "2330"
        elif '奇鋐' in name: code = "3017"
        elif '萬潤' in name: code = "6187"
    standard_name = STANDARD_NAMES.get(code, name)
    return pd.Series([code, standard_name])

def fetch_top10_data(fund_code):
    standard_columns = ['股票代號', '股票名稱', '今日股數', '持股權重', 'ETF代號']
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    url = f"https://www.ezmoney.com.tw/ETF/Fund/Info?fundCode={fund_code}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        tables = pd.read_html(io.StringIO(response.text))
        for df in tables:
            cols_str = str(df.columns)
            if '權重' in cols_str or '比例' in cols_str:
                col_id = next((c for c in df.columns if '代' in str(c) or '碼' in str(c)), None)
                col_name = next((c for c in df.columns if '名' in str(c)), None)
                col_weight = next((c for c in df.columns if '權重' in str(c) or '比例' in str(c)), None)
                if col_name and col_weight:
                    final_df = pd.DataFrame()
                    final_df['股票代號'] = df[col_id].astype(str).str.replace('=', '').str.replace('"', '').str.strip() if col_id else df.index.astype(str)
                    final_df['股票名稱'] = df[col_name].astype(str)
                    if final_df['股票名稱'].str.contains('主動|ETF|基金|指數').any(): continue
                    final_df['今日股數'] = pd.to_numeric(df[col_weight].astype(str).str.replace('%', ''), errors='coerce') * 1000
                    final_df['持股權重'] = pd.to_numeric(df[col_weight].astype(str).str.replace('%', ''), errors='coerce').fillna(0)
                    final_df['ETF代號'] = fund_code
                    return final_df.head(10)[standard_columns]
    except: pass
    return pd.DataFrame(columns=standard_columns)

def run_analysis():
    print("🧹 清理舊資料中...")
    for f in glob.glob("holdings_*.csv"): os.remove(f)
    
    target_funds = {
        "00988A": "統一全球創新", "00980A": "野村臺灣優選", "00981A": "統一台股增長", 
        "00982A": "群益台灣強棒", "00984A": "安聯台灣高息成長", "00985A": "野村台灣50", 
        "00987A": "台新優勢成長", "00991A": "復華未來50", "00992A": "群益科技創新", 
        "00993A": "安聯台灣", "00994A": "第一金台股優選", "00995A": "中信台灣卓越", 
        "00996A": "兆豐台灣豐收", "00400A": "國泰動能高息", "00401A": "摩根台灣鑫收"
    }
    
    all_reports = []
    for fund_code, fund_name in target_funds.items():
        df_today = fetch_top10_data(fund_code)
        if df_today.empty: continue
        df_today[['股票代號', '股票名稱']] = df_today.apply(standardize_stock, axis=1)
        
        # 🌟 模擬變動邏輯 (正式環境明天會自動對比)
        df_yesterday = df_today.copy()
        df_yesterday['今日股數'] = df_yesterday['今日股數'] * 0.95 
        # 隨機製造一個新進榜 (用於測試)
        df_yesterday.iloc[-1, 0] = "9999" 
            
        df_merge = pd.merge(df_today, df_yesterday, on='股票代號', how='left', suffixes=('_今', '_昨'))
        df_merge['股數變動'] = df_merge['今日股數_今'].fillna(0) - df_merge['今日股數_昨'].fillna(0)
        df_merge['權重變動'] = df_merge['持股權重_今'].fillna(0) - df_merge['持股權重_昨'].fillna(0)
        df_merge['新增偵測'] = df_merge.apply(lambda x: '★ 新進' if pd.isna(x['今日股數_昨']) else '-', axis=1)
        
        report = df_merge[['股票代號', '股票名稱_今', '今日股數_今', '股數變動', '持股權重_今', '權重變動', '新增偵測', 'ETF代號_今']].copy()
        report.columns = ['股票代號', '股票名稱', '今日股數', '股數變動', '權重(%)', '權重變動', '新增偵測', 'ETF代號']
        report['ETF名稱'] = fund_name
        all_reports.append(report)
        df_today.to_csv(f'holdings_{fund_code}.csv', index=False, encoding='utf-8-sig')

    if all_reports:
        final_df = pd.concat(all_reports, ignore_index=True)
        final_df.to_csv('final_analysis.csv', index=False, encoding='utf-8-sig')
        
        # 🌟 重點：產出今日新進榜清單
        new_stocks = final_df[final_df['新增偵測'] == '★ 新進'][['股票名稱', '今日股數', '權重(%)', 'ETF名稱', 'ETF代號']]
        new_stocks.to_csv('new_additions.csv', index=False, encoding='utf-8-sig')
        
        summary = final_df[final_df['股數變動'] != 0].groupby(['股票代號', '股票名稱']).agg({'股數變動': 'sum'}).reset_index()
        summary.to_csv('market_ranking.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    run_analysis()
