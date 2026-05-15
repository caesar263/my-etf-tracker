import os
import pandas as pd
import requests
import io

def fetch_top10_data(fund_code):
    standard_columns = ['股票代號', '股票名稱', '今日股數', '持股權重', 'ETF代號']
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # 🌟 統一投信的真實抓取邏輯
    if fund_code in ["00981A", "00988A", "00403A"]:
        url = f"https://www.ezmoney.com.tw/ETF/Fund/Info?fundCode={fund_code}"
        try:
            response = requests.get(url, headers=headers, timeout=15)
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
                    final_df['今日股數'] = pd.to_numeric(temp_df.iloc[:, 2].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
                    final_df['持股權重'] = pd.to_numeric(temp_df.iloc[:, 3].astype(str).str.replace('%', ''), errors='coerce').fillna(0)
                    final_df['ETF代號'] = fund_code
                    return final_df[standard_columns]
        except Exception as e:
            print(f"抓取 {fund_code} 失敗: {e}")
    
    # 🌟 若非統一投信，給予明確的「建置中」提示，絕不使用假資料
    return pd.DataFrame({
        '股票代號': ['-'],
        '股票名稱': ['尚未串接真實網址'],
        '今日股數': [0],
        '持股權重': [0.0],
        'ETF代號': [fund_code]
    })[standard_columns]

def run_analysis():
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

        if os.path.exists(save_path):
            df_yesterday = pd.read_csv(save_path, dtype={'股票代號': str})
            
            # 🔥 智慧清除：只要發現舊檔案裡有 1500000 這個假數字，就直接重置！
            if '今日股數' in df_yesterday.columns and (df_yesterday['今日股數'] == 1500000).any():
                print(f"🧹 自動清除 {fund_code} 的歷史假資料...")
                df_yesterday = pd.DataFrame(columns=['股票代號', '股票名稱', '今日股數', '持股權重', 'ETF代號'])
            
            # 確保舊資料不會缺少欄位
            for col in ['股票代號', '股票名稱', '今日股數', '持股權重', 'ETF代號']:
                if col not in df_yesterday.columns:
                    df_yesterday[col] = None

            df_merge = pd.merge(df_today, df_yesterday, on='股票代號', how='left', suffixes=('_今', '_昨'))
            df_merge['股數變動'] = df_merge['今日股數_今'].fillna(0) - df_merge['今日股數_昨'].fillna(0)
            df_merge['權重變動'] = df_merge['持股權重_今'].fillna(0) - df_merge['持股權重_昨'].fillna(0)
            df_merge['新增偵測'] = df_merge.apply(lambda x: '★ 新進' if pd.isna(x['今日股數_昨']) and x['股票代號'] != '-' else '-', axis=1)
            
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
        
        # 只有在「有真實資料」時才寫入存檔，不再儲存假資料
        if not df_today['股票代號'].eq('-').all():
            df_today.to_csv(save_path, index=False, encoding='utf-8-sig')

    if all_reports:
        final_df = pd.concat(all_reports, ignore_index=True)
        final_df.to_csv('final_analysis.csv', index=False, encoding='utf-8-sig')
        
        # 買賣超排行榜只計算真實股票，排除「尚未串接」的提示行
        real_data = final_df[(final_df['股票代號'] != '-') & (final_df['股數變動'] != 0)]
        if not real_data.empty:
            summary = real_data.groupby(['股票代號', '股票名稱']).agg({'股數變動': 'sum'}).reset_index()
            summary.to_csv('market_ranking.csv', index=False, encoding='utf-8-sig')
        else:
            pd.DataFrame(columns=['股票代號', '股票名稱', '股數變動']).to_csv('market_ranking.csv', index=False)

if __name__ == "__main__":
    run_analysis()
