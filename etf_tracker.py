import os
import pandas as pd

def fetch_top10_data(fund_code):
    # 定義監控標的及其成分股代號
    seeds = {
        "00988A": ["2330", "2317", "2454", "6669", "3231", "2382", "2308", "2881", "2303", "3711"],
        "00992A": ["2330", "2454", "2317", "2379", "3034", "3035", "2303", "3711", "2408", "2308"],
        "00994A": ["2330", "2317", "2412", "2308", "2881", "2882", "2886", "2002", "1301", "1303"],
        "00981A": ["2330", "2454", "3661", "3443", "5274", "6669", "3034", "3035", "2379", "6415"]
    }
    
    names = seeds.get(fund_code, seeds["00988A"])
    
    # 🌟 建立完整的股票名稱對照表，將「成分股_xxxx」替換為正式名稱
    stock_name_map = {
        "2330": "台積電", "2317": "鴻海", "2454": "聯發科", "6669": "緯穎",
        "3231": "緯創", "2382": "廣達", "2308": "台達電", "2881": "富邦金",
        "2303": "聯電", "3711": "日月光投控", "2379": "瑞昱", "3034": "聯詠",
        "3035": "智原", "2408": "南亞科", "2412": "中華電", "2882": "國泰金",
        "2886": "兆豐金", "2002": "中鋼", "1301": "台塑", "1303": "南亞",
        "3661": "世芯-KY", "3443": "創意", "5274": "信驊", "6415": "矽力*-KY"
    }
    
    data = {
        '股票代號': names,
        '股票名稱': [stock_name_map.get(n, f"成分股_{n}") for n in names],
        '股數': [1500000] * 10,
        '持股權重': [10.0] * 10
    }
    
    df = pd.DataFrame(data)
    df['股票代號'] = df['股票代號'].astype(str)
    return df

def run_analysis():
    # 監控清單
    target_funds = ["00988A", "00992A", "00994A", "00981A"]
    all_reports = []

    for fund in target_funds:
        df_today = fetch_top10_data(fund)
        save_path = f'holdings_{fund}.csv'

        if os.path.exists(save_path):
            df_yesterday = pd.read_csv(save_path, dtype={'股票代號': str})
            df_merge = pd.merge(df_today, df_yesterday, on='股票代號', how='left', suffixes=('_今', '_昨'))
            
            # 計算變動量
            df_merge['股數變動'] = df_merge['股數_今'].fillna(0) - df_merge['股數_昨'].fillna(0)
            df_merge['權重變動'] = df_merge['持股權重_今'].fillna(0) - df_merge['持股權重_昨'].fillna(0)
            df_merge['新增偵測'] = df_merge.apply(lambda x: '★ 新進榜' if pd.isna(x['股數_昨']) else '-', axis=1)
            
            # 選擇正確欄位，優先使用今日名稱
            name_col = '股票名稱_今' if '股票名稱_今' in df_merge.columns else '股票名稱'
            vol_col = '股數_今' if '股數_今' in df_merge.columns else '股數'
            weight_col = '持股權重_今' if '持股權重_今' in df_merge.columns else '持股權重'

            report = df_merge[['股票代號', name_col, vol_col, '股數變動', weight_col, '權重變動', '新增偵測']].copy()
            report.columns = ['股票代號', '股票名稱', '今日股數', '股數變動', '權重(%)', '權重變動', '新增偵測']
            report['ETF代號'] = fund
        else:
            # 第一次執行初始化
            report = df_today.copy()
            report['股數變動'] = 0
            report['權重變動'] = 0
            report['新增偵測'] = '初始化'
            report = report[['股票代號', '股票名稱', '股數', '股數變動', '持股權重', '權重變動', '新增偵測']]
            report.columns = ['股票代號', '股票名稱', '今日股數', '股數變動', '權重(%)', '權重變動', '新增偵測']
            report['ETF代號'] = fund

        all_reports.append(report)
        # 存檔供下次比對
        df_today['ETF代號'] = fund
        df_today.to_csv(save_path, index=False, encoding='utf-8-sig')

    if all_reports:
        final_df = pd.concat(all_reports, ignore_index=True)
        final_df.to_csv('final_analysis.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    run_analysis()
