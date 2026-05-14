import os
import pandas as pd

def fetch_etf_holdings():
    # 這裡已補齊 7 個標的，確保長度完全一致，並使用英文半形符號
    data = {
        '證券代號': ['2330', '2317', '2454', '00988A', '00981A', '0050', '0056'],
        '證券名稱': ['台積電', '鴻海', '聯發科', '統一全球創新', '元大高收入', '元大台灣50', '元大高股息'],
        '持股股數': [1505000, 798000, 305000, 52000, 400000, 100000, 80000], 
        '持股比例': [28.6, 11.9, 9.4, 4.7, 3.2, 5.0, 4.5],
        '產業類別': ['半導體', '其他電子', '半導體', '電腦週邊', '電腦週邊', '指數型', '指數型']
    }
    return pd.DataFrame(data)

def run_analysis():
    df_today = fetch_etf_holdings()
    
    if os.path.exists('last_data.csv'):
        df_yesterday = pd.read_csv('last_data.csv')
        df_merge = pd.merge(df_today, df_yesterday, on='證券代號', how='outer', suffixes=('_今', '_昨'))
        
        # 1. 持股比例上升(下降)
        df_merge['比例變動'] = df_merge['持股比例_今'].fillna(0) - df_merge['持股比例_昨'].fillna(0)
        
        # 2. 增(減)張數
        df_merge['增減張數'] = (df_merge['持股股數_今'].fillna(0) - df_merge['持股股數_昨'].fillna(0)) / 1000
        
        # 3. 判斷變動狀態 (新增類股/個股)
        df_merge['變動狀態'] = df_merge.apply(
            lambda x: '✨ 新增' if pd.isna(x['持股股數_昨']) else ('❌ 剔除' if pd.isna(x['持股股數_今']) else '持平'), 
            axis=1
        )
        
        # 整理最終表單
        report = df_merge[['證券代號', '證券名稱_今', '比例變動', '增減張數', '產業類別_今', '變動狀態']].copy()
        report.columns = ['證券代號', '證券名稱', '比例變動(%)', '增減張數', '產業類別', '狀態']
        
        # 儲存分析結果與排行榜
        report.to_csv('analysis_result.csv', index=False)
        report.sort_values(by='增減張數', ascending=False).to_csv('top_ranking.csv', index=False)
    
    # 儲存今日數據供明日比對
    df_today.to_csv('last_data.csv', index=False)

if __name__ == "__main__":
    run_analysis()
