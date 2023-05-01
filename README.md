#  巴哈上的動畫資料抓取分析


這是一個利用 Python 寫的爬蟲程式，可以抓取巴哈動畫網站中名字，開播時間，觀看次數，影片位址等，程式會將資料儲存至巴哈動畫.csv 檔案。並透過 Seaborn 套件繪製出指定不同年份前幾名觀看次數最高的影片資訊，以及各月份觀看次數的分佈。此專案可以幫助使用者了解獲取巴哈動畫網站上熱門動畫的觀看數、評分等數據，方便讓人快速知道有哪些動畫很紅，可以觀看

&emsp;

### 資料
![image](https://github.com/PDK9574/anime/blob/main/images/crawler_data.png)
### 圖表
![image](https://github.com/PDK9574/anime/blob/main/images/viewRank.png)


# 快速開始

### 執行 _Crawler.py
```python=
# 爬蟲參數設定
# 搜尋最大頁數
maxPage = 5
# 圖表參數
# 輸出搜尋資料中每一年份前幾筆觀看次數最高 <=20
num =  5
# 要查的年份 <=4
selected_years = ["2023","2022"]
```
## 改變年份或筆數限制

```python =
if num > 20 or len(selected_years) > 4:
    return 0
```

## 產生圖表
```python =
# 設定圖表大小
plt.figure(figsize=(20, 20))
# 繪製長條圖
# 設定標題和軸標籤
sns.catplot(data=outputDf.dropna(),x="month",  y='viewNum',hue="themeName" ,col ="year", palette='colorblind',kind="bar",col_wrap=2)
plt.suptitle(f"不同年份前{num}筆觀看次數最高的影片")
plt.xlabel('month')
plt.ylabel('viewNum')
```
