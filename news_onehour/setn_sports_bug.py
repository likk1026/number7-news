# # -*- coding: utf-8 -*-
# """
# Created on Wed Oct 16 21:23:02 2024

# @author: USER
# """

# import requests

# from bs4 import BeautifulSoup

# url = "https://www.setn.com/ViewAll.aspx?pagegroupid=34"

# data = requests.get(url)
# data.encoding= 'utf-8'
# data = data.text

# soup = BeautifulSoup(data,'html.parser')

# allNews = soup.find(id='NewsList')

# div = allNews.find_all(class_='col-sm-12 newsItems')

# for row in div:
#     a = row.find_all('a')
#     item = a[0].text
#     link = a[1].get('href')
    
#     photo = "https://attach.setn.com/images/2018_logo_B.png"
    
#     if not ('https' in link):
#         link = "https://www.setn.com" + link
#     title = a[1].text
#     print(title)
#     # print(item)
#     print(link)
#     print(photo)
#     print()
    

import requests
from bs4 import BeautifulSoup
import db  # Importing the db module

# 目標網址
url = "https://www.setn.com/ViewAll.aspx?pagegroupid=34"

# 設定 headers 模擬瀏覽器
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 發送請求
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'
html = response.text

# 解析 HTML
soup = BeautifulSoup(html, 'html.parser')

# 找到所有新聞項目，根據 class 屬性
news_section = soup.find_all(class_="newsItems")

for news in news_section:
    try:
        # 取得第一個 a 標籤 (包含圖片的連結)
        first_a_tag = news.find_all('a')[0]
        img_tag = first_a_tag.find('img')  # 獲取 img 標籤
        photo = img_tag.get('src') if img_tag else "https://www.setn.com/images/logo.png"  # 預設圖片

        # 取得第二個 a 標籤 (包含標題的連結)
        second_a_tag = news.find_all('a')[1]
        title = second_a_tag.text.strip() if second_a_tag else "無標題"
        
        # 取得連結
        link = second_a_tag.get('href') if second_a_tag else None
        if link and not link.startswith("https"):
            link = "https://star.setn.com" + link  # 補全網址

        # 插入資料到資料庫
        if title and link:
            sql = "SELECT id FROM news WHERE platform = %s AND title = %s"
            db.cursor.execute(sql, ("Setn", title))
            existing_news = db.cursor.fetchone()

            if not existing_news:
                # 插入新聞到資料庫
                sql = """
                INSERT INTO news (platform, type, title, link, img) 
                VALUES (%s, %s, %s, %s, %s)
                """
                db.cursor.execute(sql, ("SETN", "體育", title, link, photo))
                db.conn.commit()
                print(f"✅ 新增新聞: {title}")
            else:
                print(f"⚠️ 已存在: {title}")
        

    except Exception as e:
        print(f"❌ 發生錯誤: {e}")

db.cursor.close()
db.conn.close()