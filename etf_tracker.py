import os
import pandas as pd
import requests
import io

def fetch_top10_data(fund_code):
    standard_columns = ['股票代號', '股票名稱', '今日股數', '持股權重', 'ETF代號']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    # 🌟 投信網址路由表
    url_map = {
        "00981A": "https://www.ezmoney.com.tw/ETF/Fund/Info?fundCode=00981A",
        "00988A": "https://www.ezmoney.com.tw/ETF/Fund/Info?fundCode=00988A",
        "00403A": "https://www.ezmoney.com.tw/ETF/Fund/Info?fundCode=00403A",
        "00992A": "https://www.capitalfund.com.tw/etf/product/detail/500/basic",
        "00996A": "https://www.megafunds.com.tw/MEGA/etf/etf_product.aspx?id=23"
    }
    
    target_url = url_map.get(fund_code)
    
    if target_url:
        try:
            print(f"正在嘗試連線並抓取: {fund_code} ...")
            response = requests.get(target_url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            tables = pd.read_html(io.StringIO(response.text))
            
            for df in tables:
                cols_str = str(df.columns)
                first_row_str = str(df.iloc[0].values) if not df.empty else ""
                
                if ('權重' in cols_str or '比例' in cols_str) or ('權重' in first_row_str or '比例' in first_row_str):
                    
                    if '權重' in first_row_str or '比例' in first_row_str:
                        df.columns = df.iloc[0]
                        df = df[1:]
                        
                    col_id = next((c for c in df.columns if '代' in str(c) or '碼' in str(c)), None)
                    col_name = next((c for c in df.columns if '名' in str(c)), None)
                    col_vol = next((c for c in df.columns if '股數' in str(c) or '張' in str(c)), None)
                    col_weight = next((c for c in df.columns if '權重' in str(c) or '比例' in str(c)), None)
                    
                    if col_id and col_name and col_weight:
                        final_df = pd.DataFrame()
                        final_df['股票代號'] = df[col_id].astype(str).str.replace('=', '').str.replace('"', '').str.strip()
                        final_df['股票名稱'] = df[col_name].astype(str).str.strip()
                        
                        final_df = final_df[~final_df['股票代號'].isin(['nan', 'None', '-'])]
                        if final_df.empty: continue
                        
                        if final_df['股票名稱'].str.contains('主動|ETF|基金|指數|現金').any():
                            continue
                            
                        if col_vol:
                            final_df['今日股數'] = pd.to_numeric(df[col_vol].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
                        else:
                            final_df['今日股數'] = 0
                            
                        final_df['持股權重'] = pd.to_numeric(df[col_weight].astype(str).str.replace('%', ''), errors='coerce').fillna(0)
                        final_df['ETF代號'] = fund_code
                        
                        print(f"✅ {fund_code} 抓取成功！")
                        return final_df.head(10)[standard_columns]
        except Exception as e:
            print(f"❌ 抓取 {fund_code} 發生錯誤: {e}")
    else:
        print(f"⚠️ {fund_code} 尚未設定網址。")
        
    return pd.DataFrame(columns=standard_columns)

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
        
        if df_today.empty:
            continue

        if os.path.exists(save_path):
            df_yesterday = pd.read_csv(save_path, dtype={'股票代號': str})
            df_yesterday.columns = ['股票代號', '股票名稱', '今日股數', '持股權重', 'ETF代號']
            df_merge = pd.merge(df_today, df_yesterday, on='股票代號', how='left', suffixes=('_今', '_昨'))
            
            df_merge['股數變動'] = df_merge['今日股數_今'].fillna(0) - df_merge['今日股數_昨'].fillna(0)
            df_merge['權重變動'] = df_merge['持股權重_今'].fillna(0) - df_merge['持股權重_昨'].fillna(0)
            df_merge['新增偵測'] = df_merge.apply(lambda x: '★ 新進' if pd.isna(x['今日股數_昨']) else '-', axis=1)
            
            report = df_merge[['股票代號', '股票名稱_今', '今日股數_今', '股數變動', '持股權重_今', '權重變動', '新增偵測', 'ETF代號_今']].copy()
            # 確保這裡的引號和括號完整無缺
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
        final_df.to_csv('final_analysis.csv', index=False, encoding='utf-8-sig')
        
        real_data = final_df[(final_df['股票代號'] != '-') & (final_df['股數變動'] != 0)]
        if not real_data.empty:
            summary = real_data.groupby(['股票代號', '股票名稱']).agg({'股數變動': 'sum'}).reset_index()
            summary.to_csv('market_ranking.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    run_analysis()
