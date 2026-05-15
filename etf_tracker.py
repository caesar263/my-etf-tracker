import os
import pandas as pd

def fetch_top10_data(fund_code):
    """
    模擬抓取主動式 ETF 前十大持股。
    在這裡確保資料欄位完全正確。
    """
    print(f"--- 正在抓取 ETF: {fund_code} 的數據 ---")
    data = {
        '股票代號': ['2330', '2317', '2454', '6669', '3231', '2382', '2308', '2881', '2303', '3711'],
        '股票名稱': ['台積電', '鴻海', '聯發科', '緯穎', '緯創', '廣達', '台達電', '富邦金', '聯電', '日月光投控'],
        '股數': [1500000, 800000, 300000, 52000, 410000, 205000, 150000, 610000, 500000, 182000],
        '持股權重': [28.5, 12.1, 9.3, 4.6, 3.9, 3.6, 3.1, 2.9, 2.6, 2.3]
    }
    return pd.DataFrame(data)

def run_analysis():
    # 🌟 修改此代號即可監控不同 ETF
    target_fund = "00988A" 
    
    df_today = fetch_top10_data(target_fund)
    save_path = f'holdings_{target_fund}.csv'
    result_path = 'final_analysis.csv'

    if os.path.exists(save_path):
        print("偵測到昨日數據，正在進行對比分析...")
        df_yesterday = pd.read_csv(save_path)
        
        # 進行資料合併
        df_merge = pd.merge(df_today, df_yesterday, on='股票代號', how='left', suffixes=('_今', '_昨'))
        
        # 計算變動量
        df_merge['股數變動'] = df_merge['股數_今'].fillna(0) - df_merge['股數_昨'].fillna(0)
        df_merge['權重變動'] = df_merge['持股權重_今'].fillna(0) - df_merge['持股權重_昨'].fillna(0)
        
        # 偵測是否為新增股票
        df_merge['新增偵測'] = df_merge.apply(lambda x: '★ 新進榜' if pd.isna(x['股數_昨']) else '-', axis=1)
        
        # 整理最終顯示欄位
        report = df_merge[['股票代號', '股票名稱_今', '股數_今', '股數變動', '持股權重_今', '權重變動', '新增偵測']]
        report.columns = ['股票代號', '股票名稱', '今日股數', '股數變動', '權重(%)', '權重變動', '新增偵測']
    else:
        print("首次執行或找不到歷史數據，正在初始化資料...")
        report = df_today.copy()
        report['股數變動'] = 0
        report['權重變動'] = 0
        report['新增偵測'] = '初始化'
        report.columns = ['股票代號', '股票名稱', '今日股數', '權重(%)', 'ETF代號', '股數變動', '權重變動', '新增偵測']
        # 重新排序欄位以符合網頁預期
        report = report[['股票代號', '股票名稱', '今日股數', '股數變動', '權重(%)', '權重變動', '新增偵測']]

    # 存檔
    report.to_csv(result_path, index=False, encoding='utf-8-sig')
    df_today.to_csv(save_path, index=False, encoding='utf-8-sig')
    print("數據分析完成並已存檔。")

if __name__ == "__main__":
    try:
        run_analysis()
    except Exception as e:
        print(f"程式執行失敗，錯誤訊息: {e}")
        exit(1) # 讓 GitHub Actions 知道失敗了
