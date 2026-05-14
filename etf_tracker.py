import os
import pandas as pd

def get_real_data():
    """抓取或模擬持股數據"""
    data = {
        '證券代號': ['2330', '2317', '2454', '6669'],
        '證券名稱': ['台積電', '鴻海', '聯發科', '緯穎'],
        '持股股數': [1500000, 800000, 300000, 50000],
        '持股比例': [28.5, 12.0, 9.2, 4.5]
    }
    return pd.DataFrame(data)

def run_analysis():
    df_today = get_real_data()
    
    # 建立 Markdown 報告內容 (供 GitHub Issues 使用)
    report_content = "## 📊 ETF 持股每日變動報告\n\n"
    
    if os.path.exists('last_data.csv'):
        df_yesterday = pd.read_csv('last_data.csv')
        df_merge = pd.merge(df_today, df_yesterday, on='證券代號', how='outer', suffixes=('_今', '_昨'))
        df_merge['增減張'] = (df_merge['持股股數_今'].fillna(0) - df_merge['持股股數_昨'].fillna(0)) / 1000
        
        top_buys = df_merge.sort_values(by='增減張', ascending=False).head(5)
        report_content += "### 📈 買超排行 (張數)\n| 證券名稱 | 增減張數 |\n| :--- | :--- |\n"
        for _, row in top_buys.iterrows():
            report_content += f"| {row['證券名稱_今']} | +{row['增減張']:.1f} |\n"
    else:
        report_content += "🚀 系統初始化完成。"
    
    # 存檔供 Actions 讀取
    with open('daily_report.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    # 儲存今日數據供明日比對
    df_today.to_csv('last_data.csv', index=False)

if __name__ == "__main__":
    run_analysis()
