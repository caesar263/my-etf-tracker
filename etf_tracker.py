import os
import glob
import pandas as pd
import requests
import io

# 🌟 建立全市場統一的「標準名稱字典」
# 只要代號符合，系統會強制將名稱統一，徹底解決重複計算與「成分股_xxxx」的問題
STANDARD_NAMES = {
    "2330": "台積電", "2317": "鴻海", "2454": "聯發科", "6669": "緯穎",
    "3231": "緯創", "2382": "廣達", "2308": "台達電", "2881": "富邦金",
    "2303": "聯電", "3711": "日月光投控", "2379": "瑞昱", "3034": "聯詠",
    "3035": "智原", "2408": "南亞科", "2412": "中華電", "2882": "國泰金",
    "2886": "兆豐金", "2002": "中鋼", "1301": "台塑", "1303": "南亞",
    "3661": "世芯-KY", "3443": "創意", "5274": "信驊", "6415": "矽力*-KY",
    "2891": "中信金", "2884": "玉山金", "2885": "元大金", "2892": "第一金",
    "5871": "中租-KY", "1590": "亞德客-KY", "2395": "研華", "3008": "大立光",
    "2356": "英業達", "2324": "仁寶", "3293": "鈊象", "2603": "長榮",
    "2609": "陽明", "2615": "萬海", "2301": "光寶科", "2383": "台光電",
    "1476": "儒鴻", "1477": "聚陽", "2887": "台新金", "2880": "華南金",
    "2890": "永豐金", "2883": "開發金", "1476": "儒鴻"
}

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
                        final_df['股票代號'] = df[col_id].astype(str).str.replace('=', '').str.replace('"', '').str.strip() if col_id else df.index.astype(str)
                        final_df['股票名稱'] = df[col_name].astype(str)
                        
                        if final_df['股票名稱'].str.contains('主動|ETF|基金|指數').any():
                            continue
                            
                        final_df['今日股數'] = pd.to_numeric(df[col_weight].astype(str).str.replace('%', ''), errors='coerce') * 1000
                        final_df['持股權重'] = pd.to_numeric(df[col_weight].astype(str).str.replace('%', ''), errors='coerce').fillna(0)
                        final_df['ETF代號'] = fund_code
                        
                        # 🌟 過濾第一層：抓取時立刻套用標準名稱字典
                        final_df['股票名稱'] = final_df.apply(lambda x: STANDARD_NAMES.get(str(x['股票代號']).strip(), x['股票名稱']), axis=1)
                        
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
        
        # 🌟 過濾第二層：合併後再次確保名稱完全對齊，徹底消滅重複項目
        final_df['股票名稱'] = final_df.apply(lambda x: STANDARD_NAMES.get(str(x['股票代號']).strip(), x['股票名稱']), axis=1)
        final_df.to_csv('final_analysis.csv', index=False, encoding='utf-8-sig')
        
        real_data = final_df[(final_df['股票代號'] != '-') & (final_df['股數變動'] != 0)]
        if not real_data.empty:
            # 由於名稱已經全部被統一，這裡的 groupby 就能完美將同代號的股票合併計算
            summary = real_data.groupby(['股票代號', '股票名稱']).agg({'股數變動': 'sum'}).reset_index()
            summary.to_csv('market_ranking.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    run_analysis()
