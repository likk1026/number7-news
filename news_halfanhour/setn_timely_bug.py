# # -*- coding: utf-8 -*-
# """
# Created on Wed Oct 16 21:23:02 2024

# @author: USER
# """

# import requests

# from bs4 import BeautifulSoup

# url = "https://www.setn.com/ViewAll.aspx"

# data = requests.get(url)
# data.encoding= 'utf-8'
# data = data.text

# soup = BeautifulSoup(data,'html.parser')

# allNews = soup.find(id='NewsList')

# div = allNews.find_all(class_='col-sm-12 newsItems')

# for row in div:
#     time = row.find('time').text
#     a = row.find_all('a')
#     item = a[0].text
#     link = a[1].get('href')
    
#     photo = "https://attach.setn.com/images/2018_logo_B.png"
    
#     if not ('https' in link):
#         link = "https://www.setn.com" + link
#     title = a[1].text
#     print(title)
#     print(time)
#     # print(item)
#     print(link)
#     print(photo)
#     print()
    
    
import requests
from bs4 import BeautifulSoup
import db

# URL to scrape
url = "https://www.setn.com/ViewAll.aspx"
data = requests.get(url)
data.encoding = 'utf-8'
data = data.text

soup = BeautifulSoup(data, 'html.parser')

# 找到所有新聞列表區域
allNews = soup.find(id='NewsList')
div = allNews.find_all(class_='col-sm-12 newsItems')

# 遍歷每個新聞項目
for row in div:
    try:
        # 獲取標題和連結
        a = row.find_all('a')
        if len(a) < 2:
            continue  # 如果沒有找到預期的 a 標籤，跳過該項

        item = a[0].text.strip()  # 標題（如果需要其他字段，可擴展）
        link = a[1].get('href')
        
        # 如果連結不以 "https" 開頭，補全網址
        if not link.startswith('https'):
            link = "https://www.setn.com" + link
        
        # 預設圖片處理
        img_tag = row.find('img')
        if img_tag and img_tag.get('src'):
            photo = img_tag['src']
            if not photo.startswith('https'):
                photo = "https://www.setn.com" + photo  # 補全圖片網址
        else:
            photo = "https://attach.setn.com/images/2018_logo_B.png"  # 預設圖片

        # 檢查標題是否存在
        title = a[1].text.strip() if a else "無標題"

        # 這裡可以加入插入資料庫的程式碼，如果需要
        # 例如檢查是否已經存在相同標題的新聞，如果沒有再插入
        sql = "SELECT id FROM news WHERE platform = %s AND title = %s"
        db.cursor.execute(sql, ("Setn", title))
        existing_news = db.cursor.fetchone()

        if not existing_news:
            # 插入新聞到資料庫
            sql = """
            INSERT INTO news (platform, type, title, link, img) 
            VALUES (%s, %s, %s, %s, %s)
            """
            db.cursor.execute(sql, ("SETN", "即時", title, link, photo))
            db.conn.commit()
            print(f"✅ 新增新聞: {title}")
        else:
            print(f"⚠️ 已存在: {title}")

    except Exception as e:
        print(f"❌ 發生錯誤: {e}")

# 關閉資料庫連接
db.cursor.close()
db.conn.close()


