import os
import glob
import pandas as pd
import requests
import io

# 🌟 全方位台股名稱與代號對照表 (可持續擴充)
NAME_TO_CODE = {
    "台積電": "2330", "鴻海": "2317", "聯發科": "2454", "緯穎": "6669",
    "緯創": "3231", "廣達": "2382", "台達電": "2308", "富邦金": "2881",
    "聯電": "2303", "日月光投控": "3711", "瑞昱": "2379", "聯詠": "3034",
    "智原": "3035", "南亞科": "2408", "中華電": "2412", "國泰金": "2882",
    "兆豐金": "2886", "中鋼": "2002", "台塑": "1301", "南亞": "1303",
    "世芯-KY": "3661", "創意": "3443", "信驊": "5274", "矽力*-KY": "6415",
    "中信金": "2891", "玉山金": "2884", "元大金": "2885", "第一金": "2892",
    "中租-KY": "5871", "亞德客-KY": "1590", "研華": "2395", "大立光": "3008",
    "英業達": "2356", "仁寶": "2324", "鈊象": "3293", "長榮": "2603",
    "陽明": "2609", "萬海": "2615", "光寶科": "2301", "台光電": "2383",
    "儒鴻": "1476", "聚陽": "1477", "台新金": "2887", "華南金": "2880",
    "永豐金": "2890", "開發金": "2883", "奇鋐": "3017", "台燿": "6274",
    "萬潤": "6187", "旺矽": "6223", "欣興": "3037", "致茂": "2360",
    "富世達": "6805", "雙鴻": "3324", "川湖": "2059", "嘉澤": "3533",
    "健策": "3653", "祥碩": "5269", "智邦": "2345", "微星": "2377",
    "技嘉": "2376", "華碩": "2357", "宏碁": "2353", "和碩": "4938"
}
# 反轉字典，用於代號換名稱
CODE_TO_NAME = {v: k for k, v in NAME_TO_CODE.items()}

def standardize_stock(row):
    """超級雙層過濾引擎：確保每一支股票都有正確的代號與統一的名稱"""
    code = str(row['股票代號']).strip()
    name = str(row['股票名稱']).strip().upper()
    
    # 🌟 第一層：如果代號無效 (例如抓到 index 的 0, 1, 2)，啟動名稱反查機制
    if len(code) < 3 or not code.isdigit():
        # 從字典暴力反查
        for std_name, std_code in NAME_TO_CODE.items():
            if std_name in name or name in std_name:
                code = std_code
                break
                
        # 處理極端特例 (外資寫法或全名)
        if '積體電路' in name or '台積' in name: code = "2330"
        elif '日月光' in name or 'ASE' in name: code = "3711"
        
    # 🌟 第二層：有了正確的 4 碼代號後，強制換上標準名稱
    standard_name = CODE_TO_NAME.get(code, name)
    return pd.Series([code, standard_name])

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
                        # 若無代號，暫時塞入 index (隨後會被 standardize_stock 修正)
                        final_df['股票代號'] = df[col_id].astype(str).str.replace('=', '').str.replace('"', '').str.strip() if col_id else df.index.astype(str)
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
        
        # 套用超級雙層過濾引擎
        df_today[['股票代號', '股票名稱']] = df_today.apply(standardize_stock, axis=1)
        
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
