# import requests
# from bs4 import BeautifulSoup

# url = "https://news.cts.com.tw/international/index.html"

# # 發送請求
# response = requests.get(url)
# response.encoding = 'utf-8'
# html = response.text

# # 解析 HTML
# soup = BeautifulSoup(html, 'html.parser')

# # 找到新聞列表
# news_section = soup.find(id='newslist-top')

# if news_section:
#     articles = news_section.find_all('a')

#     for row in articles:
#         # 取得標題
#         title = row.get('title')
#         if not title:  # 如果 a 標籤內沒有 title，從內部 h2 或 p 抓
#             title_tag = row.find('h2') or row.find('p')
#             title = title_tag.text.strip() if title_tag else None
        
#         # 取得連結
#         link = row.get('href')
#         if not link or link == "#":  # 過濾無效連結
#             continue
#         if not link.startswith("http"):
#             link = "https://news.cts.com.tw" + link  # 補全網址
        
#         # 取得圖片
#         img_tag = row.find('img')
#         if img_tag:
#             photo = img_tag.get('src') or img_tag.get('data-src') or "https://www.cts.com.tw/images/2018cts/cts-logo.png"
#         else:
#             photo = "https://www.cts.com.tw/images/2018cts/cts-logo.png"

#         # 只顯示有標題或圖片的新聞
#         if title or photo:
#             print(f"標題: {title if title else '無標題'}")
#             print(f"圖片: {photo}")
#             print(f"連結: {link}")
#             print("-" * 50)


import requests
from bs4 import BeautifulSoup
import db  # 匯入 db.py，確保已經設定好 MySQL 連線

# 爬取目標網址
url = "https://news.cts.com.tw/international/index.html"

# 發送請求
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'
html = response.text

# 解析 HTML
soup = BeautifulSoup(html, 'html.parser')

# 找到新聞列表
news_section = soup.find(id='newslist-top')

if news_section:
    articles = news_section.find_all('a')

    for row in articles:
        try:
            # 取得標題
            title = row.get('title')
            if not title:
                title_tag = row.find('h2') or row.find('p')
                title = title_tag.text.strip() if title_tag else None

            # 取得連結
            link = row.get('href')
            if not link or link == "#":
                continue
            if not link.startswith("http"):
                link = "https://news.cts.com.tw" + link

            # **確保 `img_tag` 不是 None**
            img_tag = row.find('img')
            if img_tag:
                photo = img_tag.get('src') or img_tag.get('data-src') or "https://www.cts.com.tw/images/2018cts/cts-logo.png"
            else:
                photo = "https://www.cts.com.tw/images/2018cts/cts-logo.png"

            if title:
                # 查詢是否已存在相同標題的新聞
                sql = "SELECT id FROM news WHERE platform = %s AND title = %s"
                db.cursor.execute(sql, ("CTS", title))
                existing_news = db.cursor.fetchone()  

                if not existing_news:
                    # 插入新聞到資料庫
                    sql = """
                    INSERT INTO news (platform, type, title, link, img) 
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    db.cursor.execute(sql, ("CTS", "熱門", title, link, photo))
                    db.conn.commit()
                    print(f"✅ 新增新聞: {title}")
                else:
                    print(f"⚠️ 已存在: {title}")

        except Exception as e:
            print(f"❌ 發生錯誤: {e}")

# 關閉資料庫連接
db.cursor.close()
db.conn.close()