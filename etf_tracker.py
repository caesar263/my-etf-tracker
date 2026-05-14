import os
import pandas as pd

def fetch_active_etf_top10(fund_code):
    """
    這裡模擬抓取主動式 ETF (如 00988A 或 00981A) 的前十大持股。
    實務上，您可以將此處替換為從 API 或網頁抓取的真實數據。
    """
    # 模擬該 ETF 今日的前十大持股數據
    data = {
        '股票代號': ['2330', '2317', '2454', '6669', '3231', '2382', '2308', '2881', '2303', '3711'],
        '股票名稱': ['台積電', '鴻海', '聯發科', '緯穎', '緯創', '廣達', '台達電', '富邦金', '聯電', '日月光投控'],
        '股數': [1500000, 800000, 300000, 50000, 400000, 200000, 150000, 600000, 500000, 180000],
        '持股權重': [28.5, 12.0, 9.2, 4.5, 3.8, 3.5, 3.0, 2.8, 2.5, 2.2]
    }
    df = pd.DataFrame(data)
    df['ETF代號'] = fund_code
    return df

def run_analysis():
    # 您只需在這裡填入想要監控的主動式 ETF 代號
    target_fund = "00988A" 
    df_today = fetch_active_etf_top10(target_fund)
    
    file_name = f'holdings_{target_fund}.csv'
    
    if os.path.exists(file_name):
        df_yesterday = pd.read_csv(file_name)
        # 對比今日與昨日的前十大
        df_merge = pd.merge(df_today, df_yesterday, on='股票代號', how='left', suffixes=('_今', '_昨'))
        
        # 1. 計算每日變動
        df_merge['股數變動'] = df_merge['股數_今'].fillna(0) - df_merge['股數_昨'].fillna(0)
        df_merge['權重變動'] = df_merge['持股權重_今'].fillna(0) - df_merge['持股權重_昨'].fillna(0)
        
        # 2. 判斷每日是否有新增股票 (昨天不在前十名，今天進榜)
        df_merge['是否新增'] = df_merge.apply(lambda x: '✨ 新增' if pd.isna(x['股數_昨']) else '-', axis=1)
        
        # 整理輸出欄位
        result = df_merge[['股票代號', '股票名稱_今', '股數_今', '股數變動', '持股權重_今', '權重變動', '是否新增']]
        result.columns = ['股票代號', '股票名稱', '今日股數', '每日股數變動', '今日權重(%)', '每日權重變動', '新增狀態']
        
        # 儲存分析結果供 Streamlit 網頁顯示
        result.to_csv('display_result.csv', index=False)
    else:
        # 第一次執行，先建立初始資料
        df_today.to_csv('display_result.csv', index=False)
        
    # 更新存檔，供明天對比使用
    df_today.to_csv(file_name, index=False)

if __name__ == "__main__":
    run_analysis()
