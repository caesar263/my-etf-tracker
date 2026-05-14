import os
import pandas as pd

def fetch_etf_holdings():
    """
    此處為核心修改區：你可以依照想追蹤的 ETF 修改這裡的數據來源。
    實務上可替換為：return pd.read_csv("投信提供的CSV網址")
    """
    # 範例數據：請在此處修改或新增你想監控的證券代號與名稱
    current_data = {
        '證券代號': ['2330', '2317', '2454', '6669', '3231'],
        '證券名稱': ['台積電', '鴻海', '聯發科', '緯穎', '緯創'],
        '持股股數': [1505000, 798000, 305000, 52000, 400000], # 模擬今日股數
        '持股比例': [28.6, 11.9, 9.4, 4.7, 3.2],           # 模擬今日比例
        '產業類別': ['半導體', '其他電子', '半導體', '電腦週邊', '電腦週邊']
    }
    return pd.DataFrame(current_data)

def run_analysis():
    df_today = fetch_etf_holdings()
    
    if os.path.exists('last_data.csv'):
        df_yesterday = pd.read_csv('last_data.csv')
        
        # 合併新舊資料進行對比
        df_merge = pd.merge(df_today, df_yesterday, on='證券代號', how='outer', suffixes=('_今', '_昨'))
        
        # 1. 計算增(減)張數 (股數差 / 1000)
        df_merge['增減張數'] = (df_merge['持股股數_今'].fillna(0) - df_merge['持股股數_昨'].fillna(0)) / 1000
        
        # 2. 計算比例上升(下降)
        df_merge['比例變動'] = df_merge['持股比例_今'].fillna(0) - df_merge['持股比例_昨'].fillna(0)
        
        # 3. 判斷是否為新增類股 (昨天代號不存在，今天存在)
        df_merge['狀態'] = df_merge.apply(
            lambda x: '✨ 新增個股' if pd.isna(x['持股股數_昨']) else ('❌ 已剔除' if pd.isna(x['持股股數_今']) else '維持'), 
            axis=1
        )
        
        # 整理最終表單欄位
        final_report = df_merge[['證券代號', '證券名稱_今', '產業類別_今', '比例變動', '增減張數', '狀態']].copy()
        final_report.columns = ['證券代號', '證券名稱', '產業類別', '比例變動(%)', '增減張數', '變動狀態']
        
        # 4. 買賣超排行榜 (取前 5 名)
        ranking = final_report.sort_values(by='增減張數', ascending=False).head(5)
        
        # 儲存結果供網頁讀取
        final_report.to_csv('analysis_result.csv', index=False)
        ranking.to_csv('top_ranking.csv', index=False)
    
    # 儲存今日原始數據供明天比對
    df_today.to_csv('last_data.csv', index=False)

if __name__ == "__main__":
    run_analysis()
