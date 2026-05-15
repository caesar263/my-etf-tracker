import os
import pandas as pd

def fetch_top10_data(fund_code):
    # 模擬抓取數據，並確保『股票代號』一律為字串
    data = {
        '股票代號': ['2330', '2317', '2454', '6669', '3231', '2382', '2308', '2881', '2303', '3711'],
        '股票名稱': ['台積電', '鴻海', '聯發科', '緯穎', '緯創', '廣達', '台達電', '富邦金', '聯電', '日月光投控'],
        '股數': [1500000, 800000, 300000, 52000, 410000, 205000, 150000, 610000, 500000, 182000],
        '持股權重': [28.5, 12.1, 9.3, 4.6, 3.9, 3.6, 3.1, 2.9, 2.6, 2.3]
    }
    df = pd.DataFrame(data)
    df['股票代號'] = df['股票代號'].astype(str)
    return df

def run_analysis():
    target_fund = "00988A" 
    df_today = fetch_top10_data(target_fund)
    save_path = f'holdings_{target_fund}.csv'
    result_path = 'final_analysis.csv'

    if os.path.exists(save_path):
        # 關鍵修正：讀取時強制指定為字串，避免 2330 變成數字
        df_yesterday = pd.read_csv(save_path, dtype={'股票代號': str})
        
        # 確保今日數據也是字串，才進行合併
        df_today['股票代號'] = df_today['股票代號'].astype(str)
        
        df_merge = pd.merge(df_today, df_yesterday, on='股票代號', how='left', suffixes=('_今', '_昨'))
        
        df_merge['股數變動'] = df_merge['股數_今'].fillna(0) - df_merge['股數_昨'].fillna(0)
        df_merge['權重變動'] = df_merge['持股權重_今'].fillna(0) - df_merge['持股權重_昨'].fillna(0)
        df_merge['新增偵測'] = df_merge.apply(lambda x: '★ 新進榜' if pd.isna(x['股數_昨']) else '-', axis=1)
        
        report = df_merge[['股票代號', '股票名稱_今', '股數_今', '股數變動', '持股權重_今', '權重變動', '新增偵測']]
        report.columns = ['股票代號', '股票名稱', '今日股數', '股數變動', '權重(%)', '權重變動', '新增偵測']
    else:
        # 初始化資料
        report = df_today.copy()
        report['股數變動'] = 0
        report['權重變動'] = 0
        report['新增偵測'] = '初始化'
        report = report[['股票代號', '股票名稱', '股數', '股數變動', '持股權重', '權重變動', '新增偵測']]
        report.columns = ['股票代號', '股票名稱', '今日股數', '股數變動', '權重(%)', '權重變動', '新增偵測']

    # 存檔時使用 utf-8-sig 確保中文不亂碼
    report.to_csv(result_path, index=False, encoding='utf-8-sig')
    df_today.to_csv(save_path, index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    run_analysis()
