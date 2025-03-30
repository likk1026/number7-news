import requests
from bs4 import BeautifulSoup
import db  # 匯入 db.py，確保已經設定好 MySQL 連線

# 爬取目標網址
url = "https://news.cts.com.tw/real/index.html"

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

            # 取得圖片
            img_tag = row.find('img')
            photo = (
                img_tag.get('src')
                or img_tag.get('data-src')
                or "https://www.cts.com.tw/images/2018cts/cts-logo.png"
            )

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
                    db.cursor.execute(sql, ("CTS", "即時", title, link, photo))
                    db.conn.commit()
                    print(f"✅ 新增新聞: {title}")
                else:
                    print(f"⚠️ 已存在: {title}")

        except Exception as e:
            print(f"❌ 發生錯誤: {e}")

# 關閉資料庫連接
db.cursor.close()
db.conn.close()
