import os
import pandas as pd

def fetch_active_etf_top10():
    # 您可以在此修改資料，模擬不同日期的前 10 大變動
    # 這裡確保資料長度為 10，且格式正確
    data = {
        '股票代號': ['2330', '2317', '2454', '6669', '3231', '2382', '2308', '2881', '2303', '3711'],
        '股票名稱': ['台積電', '鴻海', '聯發科', '緯穎', '緯創', '廣達', '台達電', '富邦金', '聯電', '日月光投控'],
        '股數': [1500000, 800000, 300000, 52000, 410000, 205000, 150000, 610000, 500000, 182000],
        '持股權重': [28.5, 12.1, 9.3, 4.6, 3.9, 3.6, 3.1, 2.9, 2.6, 2.3]
    }
    return pd.DataFrame(data)

def run_analysis():
    df_today = fetch_active_etf_top10()
    save_file = 'last_top10.csv'
    display_file = 'analysis_result.csv'
    
    if os.path.exists(save_file):
        df_yesterday = pd.read_csv(save_file)
        # 對比邏輯
        df_merge = pd.merge(df_today, df_yesterday, on='股票代號', how='left', suffixes=('_今', '_昨'))
        
        # 計算變動
        df_merge['股數變動'] = df_merge['股數_今'].fillna(0) - df_merge['股數_昨'].fillna(0)
        df_merge['權重變動'] = df_merge['持股權重_今'].fillna(0) - df_merge['持股權重_昨'].fillna(0)
        
        # 判斷是否為新增股票 (昨日不在前十名中)
        df_merge['新增狀態'] = df_merge.apply(lambda x: '✨ 新進榜' if pd.isna(x['股數_昨']) else '-', axis=1)
        
        # 整理欄位
        report = df_merge[['股票代號', '股票名稱_今', '股數_今', '股數變動', '持股權重_今', '權重變動', '新增狀態']]
        report.columns = ['股票代號', '股票名稱', '今日股數', '股數變動', '今日權重(%)', '權重變動', '新增狀態']
        report.to_csv(display_file, index=False)
    else:
        # 第一次執行，建立基礎資料
        df_today.to_csv(display_file, index=False)
        
    df_today.to_csv(save_file, index=False)

if __name__ == "__main__":
    run_analysis()
