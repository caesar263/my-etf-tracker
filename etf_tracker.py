import os
import pandas as pd
import requests
import io

def fetch_top10_data(fund_code):
    standard_columns = ['股票代號', '股票名稱', '今日股數', '持股權重', 'ETF代號']
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # 🌟 投信網址路由表：為不同投信配置專屬的抓取網址
    url_map = {
        "00981A": f"https://www.ezmoney.com.tw/ETF/Fund/Info?fundCode={fund_code}", # 統一
        "00988A": f"https://www.ezmoney.com.tw/ETF/Fund/Info?fundCode={fund_code}", # 統一
        "00403A": f"https://www.ezmoney.com.tw/ETF/Fund/Info?fundCode={fund_code}", # 統一
        # 未來若取得群益、野村等投信的持股公告網址，可直接新增於此
    }
    
    target_url = url_map.get(fund_code)
    
    if target_url:
        try:
            response = requests.get(target_url, headers=headers, timeout=15)
            tables = pd.read_html(io.StringIO(response.text))
            
            for df in tables:
                cols = str(df.columns)
                if ('權重' in cols or '比例' in cols) and ('淨值' not in cols):
                    temp_df = df.head(10).copy()
                    final_df = pd.DataFrame()
                    final_df['股票代號'] = temp_df.iloc[:, 0].astype(str)
                    final_df['股票名稱'] = temp_df.iloc[:, 1].astype(str)
                    
                    if final_df['股票名稱'].str.contains('主動|ETF|基金|指數').any():
                        continue
                        
                    # 清洗數字格式
                    final_df['今日股數'] = pd.to_numeric(temp_df.iloc[:, 2].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
                    final_df['持股權重'] = pd.to_numeric(temp_df.iloc[:, 3].astype(str).str.replace('%', ''), errors='coerce').fillna(0)
                    final_df['ETF代號'] = fund_code
                    return final_df[standard_columns]
        except Exception as e:
            print(f"❌ 抓取 {fund_code} 真實數據失敗: {e}")
    else:
        print(f"⚠️ {fund_code} 尚未設定對應的投信官網網址，跳過抓取。")
        
    # 🌟 嚴格規定：抓不到就回傳空表，絕不使用 1500000 假數據污染排行
    return pd.DataFrame(columns=standard_columns)

def run_analysis():
    # 🌟 根據您提供的圖片，完整建檔 14 檔最新主動式 ETF
    target_funds = {
        "00980A": "野村臺灣優選", "00981A": "統一台股增長", "00982A": "群益台灣強棒",
        "00984A": "安聯台灣高息成長", "00985A": "野村台灣50", "00987A": "台新優勢成長",
        "00991A": "復華未來50", "00992A": "群益科技創新", "00993A": "安聯台灣",
        "00994A": "第一金台股優選", "00995A": "中信台灣卓越", "00996A": "兆豐台灣豐收",
        "00400A": "國泰動能高息", "00401A": "摩根台灣鑫收"
    }
    
    all_reports = []
    for fund_code, fund_name in target_funds.items():
        df_today = fetch_top10_data(fund_code)
        save_path = f'holdings_{fund_code}.csv'
        
        if df_today.empty:
            continue # 如果是空資料（抓不到），直接跳過不存檔，避免覆蓋舊的真實數據

        if os.path.exists(save_path):
            df_yesterday = pd.read_csv(save_path, dtype={'股票代號': str})
            df_yesterday.columns = ['股票代號', '股票名稱', '今日股數', '持股權重', 'ETF代號']
            df_merge = pd.merge(df_today, df_yesterday, on='股票代號', how='left', suffixes=('_今', '_昨'))
            
            df_merge['股數變動'] = df_merge['今日股數_今'].fillna(0) - df_merge['今日股數_昨'].fillna(0)
            df_merge['權重變動'] = df_merge['持股權重_今'].fillna(0) - df_merge['持股權重_昨'].fillna(0)
            df_merge['新增偵測'] = df_merge.apply(lambda x: '★ 新進' if pd.isna(x['今日股數_昨']) else '-', axis=1)
            
            report = df_merge[['股票代號', '股票名稱_今', '今日股數_今', '股數變動', '持股權重_今', '權重變動', '新增偵測', 'ETF代號_今']].copy()
            report.columns = ['股票代號', '股票名稱', '今日股數', '股數變動', '權重(%)', '權重變動', '新增偵測', 'ETF代號']
            report['ETF名稱'] = fund_name
        else:
            report = df_today.copy()
            report['股數變動'], report['權重變動'], report['新增偵測'] = 0, 0, '初始化'
            report['ETF名稱'] = fund_name
            report = report[['股票代號', '股票名稱', '今日股數', '股數變動', '持股權重', '權重變動', '新增偵測', 'ETF代號', 'ETF名稱']]
            report.columns = ['股票代號', '股票名稱', '今日股數', '股數變動', '權重(%)', '權重變動', '新增偵測', 'ETF代號', 'ETF名稱']

        all_reports.append(report)
        df_today.to_csv(save_path, index=False, encoding='utf-8-sig')

    if all_reports:
        final_df = pd.concat(all_reports, ignore_index=True)
        final_df = final_df[~final_df['股票名稱'].str.contains('主動|基金|ETF', na=False)]
        final_df.to_csv('final_analysis.csv', index=False, encoding='utf-8-sig')
        
        # 只統計真實有變動的股數，去除 0 變動的雜訊
        active_changes = final_df[final_df['股數變動'] != 0]
        summary = active_changes.groupby(['股票代號', '股票名稱']).agg({'股數變動': 'sum'}).reset_index()
        summary.to_csv('market_ranking.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    run_analysis()
