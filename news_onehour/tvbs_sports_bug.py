# # -*- coding: utf-8 -*-
# """
# Created on Mon Mar 24 19:31:51 2025

# @author: gt901
# """

# import requests
# import sqlite3
# from bs4 import BeautifulSoup

# conn = sqlite3.connect("news.db")
# cursor = conn.cursor()

# url ="https://news.tvbs.com.tw/sports"

# data = requests.get(url)
# data.encoding= 'utf-8'
# data = data.text

# soup = BeautifulSoup(data,'html.parser')

# newslist = soup.find(class_='news_now2')

# news = newslist.find(class_='list')

# li = news.find_all('li')

# for row in li:
#     link = row.find('a')
#     if link != None:
#         link = "https://news.tvbs.com.tw" + link.get('href')
#         photo = row.find('img').get('data-original')
#         title = row.find('h2').text
        
#         print(f"標題 :{title}")
#         print(f"圖片 :{photo}")
#         print(f"連結 :{link}")
#         print("-" *10)



import requests
from bs4 import BeautifulSoup
import db  

# 目標網址
url = "https://news.tvbs.com.tw/sports"

# 發送請求
data = requests.get(url)
data.encoding = 'utf-8'
data = data.text

# 解析 HTML
soup = BeautifulSoup(data, 'html.parser')

# 找到新聞列表
newslist = soup.find(class_='news_now2')

if newslist:
    news = newslist.find(class_='list')
    li = news.find_all('li')

    for row in li:
        link_tag = row.find('a')
        if link_tag:
            link = "https://news.tvbs.com.tw" + link_tag.get('href')
            title = row.find('h2').text.strip() if row.find('h2') else "無標題"
            img_tag = row.find('img')
            photo = img_tag.get('data-original') if img_tag else "https://defaultimage.com/default.jpg"

            sql = "SELECT id FROM news WHERE platform = %s AND title = %s"
            db.cursor.execute(sql, ("TVBS", title))
            existing_news = db.cursor.fetchone()  

            if not existing_news:
                    # 插入新聞到資料庫
                sql = """
                INSERT INTO news (platform, type, title, link, img) 
                VALUES (%s, %s, %s, %s, %s)
                """
                db.cursor.execute(sql, ("TVBS", "體育", title, link, photo))
                db.conn.commit()
                print(f"✅ 新增新聞: {title}")
            else:
                print(f"⚠️ 已存在: {title}")
else:
    print("❌ 找不到新聞列表區域")

# 關閉資料庫連接
db.cursor.close()
db.conn.close()