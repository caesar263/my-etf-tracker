import os
import pandas as pd

def fetch_top10_data(fund_code):
    """
    模擬抓取不同 ETF 的數據。
    實務上，不同 ETF 的成分股會有所不同，這裡根據代號模擬差異化數據。
    """
    # 根據代號模擬一些不同的數據，讓監控更有感
    seeds = {
        "00988A": ["2330", "2317", "2454", "6669", "3231", "2382", "2308", "2881", "2303", "3711"],
        "00992A": ["2330", "2454", "2317", "2379", "3034", "3035", "2303", "3711", "2408", "2308"],
        "00994A": ["2330", "2317", "2412", "2308", "2881", "2882", "2886", "2002", "1301", "1303"],
        "00981A": ["2330", "2454", "3661", "3443", "5274", "6669", "3034", "3035", "2379", "6415"]
    }
    
    # 如果代號不在種子裡，就用預設清單
    names = seeds.get(fund_code, seeds["00988A"])
    
    data = {
        '股票代號': names,
        '股票名稱': [f"標的_{n}" for n in names], # 實務上會是真實名稱
        '股數': [1000000 + (int(fund_code[2:5])*100)] * 10, # 模擬數據
        '持股權重': [10.0] * 10 # 模擬權重
    }
    # 為了讓 Caesar 看起來更真實，我們手動修正前幾個名稱
    real_names = {"2330": "台積電", "2317": "鴻海", "2454": "聯發科", "6669": "緯穎"}
    data['股票名稱'] = [real_names.get(n, f"成分股_{n}") for n in names]
    
    df = pd.DataFrame(data)
    df['股票代號'] = df['股票代號'].astype(str)
    df['ETF代號'] = fund_code
    return df

def run_analysis():
    # 🌟 在此定義所有要監控的標的
    target_funds = ["00988A", "00992A", "00994A", "00981A"]
    all_reports = []

    for fund in target_funds:
        df_today = fetch_top10_data(fund)
        save_path = f'holdings_{fund}.csv'

        if os.path.exists(save_path):
            df_yesterday = pd.read_csv(save_path, dtype={'股票代號': str})
            df_merge = pd.merge(df_today, df_yesterday, on='股票代號', how='left', suffixes=('_今', '_昨'))
            
            df_merge['股數變動'] = df_merge['股數_今'].fillna(0) - df_merge['股數_昨'].fillna(0)
            df_merge['權重變動'] = df_merge['持股權重_今'].fillna(0) - df_merge['持股權重_昨'].fillna(0)
            df_merge['新增偵測'] = df_merge.apply(lambda x: '★ 新進榜' if pd.isna(x['股數_昨']) else '-', axis=1)
            
            report = df_merge[['股票代號', '股票名稱_今', '今日股數_今', '股數變動', '持股權重_今', '權重變動', '新增偵測', 'ETF代號_今']]
            report.columns = ['股票代號', '股票名稱', '今日股數', '股數變動', '權重(%)', '權重變動', '新增偵測', 'ETF代號']
        else:
            report = df_today.copy()
            report['股數變動'] = 0
            report['權重變動'] = 0
            report['新增偵測'] = '初始化'
            report = report[['股票代號', '股票名稱', '股數', '股數變動', '持股權重', '權重變動', '新增偵測', 'ETF代號']]
            report.columns = ['股票代號', '股票名稱', '今日股數', '股數變動', '權重(%)', '權重變動', '新增偵測', 'ETF代號']

        all_reports.append(report)
        df_today.to_csv(save_path, index=False, encoding='utf-8-sig')

    # 合併所有 ETF 的分析結果
    final_df = pd.concat(all_reports, ignore_index=True)
    final_df.to_csv('final_analysis.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    run_analysis()
