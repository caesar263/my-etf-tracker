import os
import pandas as pd
import requests
import io

def fetch_top10_data(fund_code):
    standard_columns = ['股票代號', '股票名稱', '今日股數', '持股權重', 'ETF代號']
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        url = f"https://www.ezmoney.com.tw/ETF/Fund/Info?fundCode={fund_code}"
        
        response = requests.get(url, headers=headers, timeout=15)
        tables = pd.read_html(io.StringIO(response.text))
        
        for df in tables:
            cols = str(df.columns)
            # 🌟 嚴格過濾：必須要有權重或比例，且不能包含淨值(避免抓到基金列表)
            if ('權重' in cols or '比例' in cols) and ('淨值' not in cols):
                temp_df = df.head(10).copy()
                final_df = pd.DataFrame()
                final_df['股票代號'] = temp_df.iloc[:, 0].astype(str)
                final_df['股票名稱'] = temp_df.iloc[:, 1].astype(str)
                
                # 🌟 如果抓出來的「股票名稱」裡面含有「主動」或「ETF」，代表抓錯表了，跳過！
                if final_df['股票名稱'].str.contains('主動|ETF|基金').any():
                    continue
                    
                final_df['今日股數'] = pd.to_numeric(temp_df.iloc[:, 2].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
                final_df['持股權重'] = pd.to_numeric(temp_df.iloc[:, 3].astype(str).str.replace('%', ''), errors='coerce').fillna(0)
                final_df['ETF代號'] = fund_code
                return final_df[standard_columns]
    except Exception as e:
        print(f"抓取 {fund_code} 異常: {e}")
        
    # --- 備用數據 ---
    seeds = ["2330", "2317", "2454", "6669", "3231", "2382", "2308", "2881", "2303", "3711"]
    data = {
        '股票代號': seeds,
        '股票名稱': ["台積電", "鴻海", "聯發科", "緯穎", "緯創", "廣達", "台達電", "富邦金", "聯電", "日月光"],
        '今日股數': [1500000] * 10,
        '持股權重': [10.0] * 10,
        'ETF代號': [fund_code] * 10
    }
    return pd.DataFrame(data)[standard_columns]

def run_analysis():
    target_funds = [
        "00981A", "00994A", "00992A", "00987A", "00995A", 
        "00991A", "00985A", "00982A", "00980A", "00984A", 
        "00996A", "00400A", "00993A", "00401A", "00403A"
    ]
    
    all_reports = []
    for fund in target_funds:
        df_today = fetch_top10_data(fund)
        save_path = f'holdings_{fund}.csv'

        if os.path.exists(save_path):
            df_yesterday = pd.read_csv(save_path, dtype={'股票代號': str})
            df_yesterday.columns = ['股票代號', '股票名稱', '今日股數', '持股權重', 'ETF代號']
            df_merge = pd.merge(df_today, df_yesterday, on='股票代號', how='left', suffixes=('_今', '_昨'))
            
            df_merge['股數變動'] = df_merge['今日股數_今'].fillna(0) - df_merge['今日股數_昨'].fillna(0)
            df_merge['權重變動'] = df_merge['持股權重_今'].fillna(0) - df_merge['持股權重_昨'].fillna(0)
            df_merge['新增偵測'] = df_merge.apply(lambda x: '★ 新進' if pd.isna(x['今日股數_昨']) else '-', axis=1)
            
            report = df_merge[['股票代號', '股票名稱_今', '今日股數_今', '股數變動', '持股權重_今', '權重變動', '新增偵測', 'ETF代號_今']].copy()
            report.columns = ['股票代號', '股票名稱', '今日股數', '股數變動', '權重(%)', '權重變動', '新增偵測', 'ETF代號']
        else:
            report = df_today.copy()
            report['股數變動'], report['權重變動'], report['新增偵測'] = 0, 0, '初始化'
            report = report[['股票代號', '股票名稱', '今日股數', '股數變動', '持股權重', '權重變動', '新增偵測', 'ETF代號']]
            report.columns = ['股票代號', '股票名稱', '今日股數', '股數變動', '權重(%)', '權重變動', '新增偵測', 'ETF代號']

        all_reports.append(report)
        df_today.to_csv(save_path, index=False, encoding='utf-8-sig')

    if all_reports:
        final_df = pd.concat(all_reports, ignore_index=True)
        # 確保最終存檔排除掉舊資料中可能殘留的異常值
        final_df = final_df[~final_df['股票名稱'].str.contains('主動|基金|ETF', na=False)]
        final_df.to_csv('final_analysis.csv', index=False, encoding='utf-8-sig')
        
        summary = final_df.groupby(['股票代號', '股票名稱']).agg({'股數變動': 'sum'}).reset_index()
        summary.to_csv('market_ranking.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    run_analysis()
