import time
import datetime
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from bs4 import BeautifulSoup
# 忽略字型警告
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

# 確認是否有正常連線
def CheckConnect(url, headers):
    try:
        response = requests.get(url, headers=headers)
        checkSuccess = True
        return response, checkSuccess
    except Exception as e:
        print('下載失敗!')
        response = None
        checkSuccess = False
        return response, checkSuccess


# 爬蟲參數設定
# 搜尋最大頁數
maxPage = 5
# 圖表參數
# 輸出搜尋資料中每一年份前幾筆觀看次數最高
num =  10
# 要查的年份
selected_years = ["2023","2022"]
# 迴圈搜尋結果頁數
outputDf = pd.DataFrame()

for page in range(1, maxPage+1):
    # 設定header
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
                      '(KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36'
    }
    # 目標網址
    url = "https://ani.gamer.com.tw/animeList.php?page="+str(page)+"&c=All&sort=1"

    # 取得網頁資料
    # 防呆機制
    checkSuccess = False
    tryNums = 0
    while not checkSuccess:
        response, checkSuccess = CheckConnect(url, headers)
        if not checkSuccess:   # 若爬取失敗 則暫停2秒
            if tryNums == 5:   # 若已重新爬取累計5次 則放棄此次程式執行
                break
            tryNums += 1
            print('本次下載失敗 程式暫停2秒')
            time.sleep(2)

    # 防呆機制: 若累積爬取資料失敗 則終止此次程式
    if tryNums == 5:
        print('下載失敗次數累積5次 結束程式')
        break

    # 轉為soup格式
    soup = BeautifulSoup(response.text, 'html.parser')
    # 取得搜尋動畫資料
    result = soup.select('a.theme-list-main')
    # 取得動畫名
    theme_name = [r.select('p.theme-name')[0].text.replace('\n', '').strip() for r in result]
    # 取得動畫開播時間
    theme_time = [r.select('p.theme-time')[0].text.replace('\n', '').strip() for r in result]
    # 取得動畫播放集數
    theme_num = [r.select('span.theme-number')[0].text.replace('\n', '').strip() for r in result]
    # 取得搜尋動畫資料
    view_result= soup.select('.show-view-number')
    # 取得觀看次數
    view_num = [r.select('p')[0].text.replace('\n', '').replace(" ","").strip() for r in view_result]
    # 取得影片位址
    theme_address=["https://"+r.get("href") for r in result]

    # 組合資訊成資料表並儲存
    iOutputDf = pd.DataFrame({'page':page,
                              'themeName': theme_name,
                              'themeTime': theme_time,
                              'themeNum': theme_num,
                              'viewNum': view_num,
                              'themeAddress': theme_address
                            })
    outputDf = pd.concat([outputDf, iOutputDf])
    
# 加入本次搜尋資訊
outputDf.insert(0, 'maxPage', maxPage, True)
now = datetime.datetime.now()
outputDf.insert(0, 'searchTime', now.strftime('%Y-%m-%d %H:%M:%S'), True)


# 輸出csv檔案
outputDf.to_csv('巴哈動畫.csv', encoding='utf-8-sig')

# 轉成萬元單位
def ToWan(x):
    return str(x // 10000) + '萬'
# 轉成數字單位
def ToNum(x):
    return eval(x.replace("萬","e4"))


def orderCsv(outputDf,num = 2,selected_years =[]):
    """
    函數描述：
    輸出圖表關於搜尋資料中每一年分依觀看次數排序前幾名的動畫
    參數：
    num: 每一年份前幾筆觀看次數最高 
    selected_years: 要查的年份 
    """
    if num > 20 or len(selected_years) > 4:
        return 0
    # 排序
    outputDf['viewNum'] = outputDf['viewNum'].apply(ToNum)
    # 刪除?
    outputDf=outputDf.sort_values(by=['viewNum'],ascending=False)
    # 年分
    outputDf['year'] = outputDf['themeTime'].str.extract(r'(\d{4})')
    # 月
    outputDf['month'] = outputDf['themeTime'].str.extract(r'/(\d{2})')
    # 輸出依觀看次數排序的資料年分為群組,是否符合查的年份
    outputDf = outputDf.groupby('year').apply(lambda x: x.nlargest(num, 'viewNum')).reset_index(drop=True)
    outputDf = outputDf[outputDf['year'].isin(selected_years)]
    outputDf['year_theme'] = outputDf['year'].astype(str) + '_' + outputDf['themeName']
    # 設定圖表大小
    plt.figure(figsize=(20, 20))
    # 繪製長條圖
    # 設定標題和軸標籤
    sns.catplot(data=outputDf.dropna(),x="month",  y='viewNum',hue="year_theme" ,col ="year", palette='colorblind',kind="bar",col_wrap=2)
    plt.suptitle(f"不同年份前{num}筆觀看次數最高的影片")
    plt.xlabel('month')
    plt.ylabel('viewNum')
    # 設定y軸為萬
    def format_ytick(value, _):
        if value >= 1e4:
            return f'{value/1e4:.0f} 萬'
        else:
            return int(value)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(format_ytick))
    # 字體
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
    plt.rcParams['axes.unicode_minus'] = False
    # 輸出csv檔案
    outputDf.to_csv('巴哈動畫觀看次數.csv', encoding='utf-8-sig')
    # 顯示圖表
    plt.show()
   


# 執行圖表
orderCsv(outputDf,num=num,selected_years=selected_years)



