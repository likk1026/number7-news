# import requests
# from bs4 import BeautifulSoup

# url = "https://www.ettoday.net/news/focus/%E7%84%A6%E9%BB%9E%E6%96%B0%E8%81%9E/"

# # 發送請求
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
# }
# response = requests.get(url, headers=headers)
# response.encoding = 'utf-8'
# html = response.text

# # 解析 HTML
# soup = BeautifulSoup(html, 'html.parser')

# # 找到新聞列表區域
# news_section = soup.find('div', class_='block block_1 infinite_scroll')

# if news_section:
#     articles = news_section.find_all('div', class_='piece clearfix')

#     for article in articles:
#         # 取得標題
#         title_tag = article.find('h3')  # 標題通常在 h3 裡
#         title = title_tag.text.strip() if title_tag else "無標題"

#         # 取得連結
#         link_tag = article.find('a')
#         link = link_tag['href'] if link_tag and link_tag.has_attr('href') else None
#         if link and not link.startswith("http"):
#             link = "https://www.ettoday.net" + link  # 補全網址

#         # 取得圖片
#         img_tag = article.find('img')
#         photo = img_tag['data-original'] if img_tag and img_tag.has_attr('data-original') else None
#         if not photo:
#             photo = "https://www.ettoday.net/images/logo.png"  # 預設圖片

#         # 顯示結果
#         print(f"標題: {title}")
#         print(f"圖片: {photo}")
#         print(f"連結: {link}")
#         print("-" * 50)


import requests
from bs4 import BeautifulSoup
import db

# 目標網址
url = "https://www.ettoday.net/news/focus/%E7%84%A6%E9%BB%9E%E6%96%B0%E8%81%9E/"

# 設定 headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 發送請求
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'
html = response.text

# 解析 HTML
soup = BeautifulSoup(html, 'html.parser')

# 找到新聞列表區域
news_section = soup.find('div', class_='block block_1 infinite_scroll')

if not news_section:
    print("❌ 無法找到新聞區塊，可能是 HTML 結構改變")
    exit()

articles = news_section.find_all('div', class_='piece clearfix')

for article in articles:
    try:
        # 取得標題
        title_tag = article.find('h3')
        title = title_tag.text.strip() if title_tag else "無標題"

        # 取得連結
        link_tag = article.find('a')
        link = link_tag['href'] if link_tag and link_tag.has_attr('href') else None
        if link and not link.startswith("http"):
            link = "https://www.ettoday.net" + link  # 補全網址

        # 取得圖片
        img_tag = article.find('img')
        photo = img_tag['data-original'] if img_tag and img_tag.has_attr('data-original') else (
            img_tag['src'] if img_tag and img_tag.has_attr('src') else "https://www.ettoday.net/images/logo.png"
        )

        # 過濾無效新聞
        if not title or not link:
            continue

        # 檢查新聞是否已存在
        sql = "SELECT id FROM news WHERE platform = %s AND title = %s"
        db.cursor.execute(sql, ("ETtoday", title))
        existing_news = db.cursor.fetchone()

        if not existing_news:
            # 插入新聞到資料庫
            sql = """
            INSERT INTO news (platform, type, title, link, img) 
            VALUES (%s, %s, %s, %s, %s)
            """
            db.cursor.execute(sql, ("ETtoday", "即時", title, link, photo))
            db.conn.commit()
            print(f"✅ 新增新聞: {title}")
        else:
            print(f"⚠️ 已存在: {title}")

    except Exception as e:
        print(f"❌ 發生錯誤: {e}")

# 關閉資料庫連線
db.cursor.close()
db.conn.close()
