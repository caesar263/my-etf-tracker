import os
import pandas as pd

def fetch_top10_data(fund_code):
    """
    您可以根據想追蹤的代號（如 00988A）在此更新數據。
    實務上可串接 API 或爬蟲，目前先以您要求的欄位進行範例模擬。
    """
    # 模擬該 ETF 今日的前十大持股 (長度務必為 10)
    data = {
        '股票代號': ['2330', '2317', '2454', '6669', '3231', '2382', '2308', '2881', '2303', '3711'],
        '股票名稱': ['台積電', '鴻海', '聯發科', '緯穎', '緯創', '廣達', '台達電', '富邦金', '聯電', '日月光投控'],
        '股數': [1500000, 800000, 300000, 52000, 410000, 205000, 150000, 610000, 500000, 182000],
        '持股權重': [28.5, 12.1, 9.3, 4.6, 3.9, 3.6, 3.1, 2.9, 2.6, 2.3]
    }
    df = pd.DataFrame(data)
    df['ETF代號'] = fund_code
    return df

def run_analysis():
    # 🌟 修改此處代號即可更換監控目標
    target_fund = "00988A" 
    
    df_today = fetch_top10_data(target_fund)
    save_path = f'holdings_{target_fund}.csv'
    result_path = 'final_analysis.csv'

    if os.path.exists(save_path):
        df_yesterday = pd.read_csv(save_path)
        # 對比邏輯：以今日前十名為主
        df_merge = pd.merge(df_today, df_yesterday, on='股票代號', how='left', suffixes=('_今', '_昨'))
        
        # 1. 每日股數與權重變動
        df_merge['股數變動'] = df_merge['股數_今'].fillna(0) - df_merge['股數_昨'].fillna(0)
        df_merge['權重變動'] = df_merge['持股權重_今'].fillna(0) - df_merge['持股權重_昨'].fillna(0)
        
        # 2. 判斷是否有新增股票 (昨日不在名單內)
        df_merge['每日新增'] = df_merge.apply(lambda x: '★ 新進榜' if pd.isna(x['股數_昨']) else '-', axis=1)
        
        # 整理輸出欄位
        report = df_merge[['股票代號', '股票名稱_今', '股數_今', '股數變動', '持股權重_今', '權重變動', '每日新增']]
        report.columns = ['股票代號', '股票名稱', '今日股數', '股數變動', '權重(%)', '權重變動', '新增偵測']
        report.to_csv(result_path, index=False, encoding='utf-8-sig')
    else:
        # 第一次執行，先建立存檔
        df_today.to_csv(result_path, index=False, encoding='utf-8-sig')
        
    # 更新存檔備份
    df_today.to_csv(save_path, index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    run_analysis()
