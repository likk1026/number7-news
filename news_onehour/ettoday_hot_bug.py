# import requests
# from bs4 import BeautifulSoup

# # 目標網址
# url = "https://www.ettoday.net/news/hot-news.htm"

# # 設定 User-Agent（模擬瀏覽器）
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
# }

# # 發送 GET 請求
# response = requests.get(url, headers=headers)

# # 確認請求成功
# if response.status_code == 200:
#     # 解析 HTML
#     soup = BeautifulSoup(response.text, "html.parser")

#     # 使用 .block.block_1.hot-newslist 來抓取新聞列表
#     news_list = soup.select(".block.block_1.hot-newslist .piece")

#     # 顯示結果
#     for news in news_list:
#         # 獲取標題與連結
#         title_tag = news.select_one("h3 a")
#         title = title_tag.text.strip() if title_tag else "無標題"
#         title = title.replace("\u3000", " ")#刪除標題中的空格
#         link = title_tag["href"] if title_tag else "無連結"

#         # 確保 link 是完整 URL
#         if not link.startswith("https"):
#             link = "https://www.ettoday.net" + link

#         # 獲取圖片
#         img = "https://static.ettoday.net/style/ettoday2017/images/logo_ettoday_v4.png"

#         print(f"標題: {title}")
#         print(f"圖片: {img}")
#         print(f"連結: {link}")
#         print("-" * 50)


import requests
from bs4 import BeautifulSoup
import db  # 匯入 db.py 來操作資料庫

# 目標網址
url = "https://www.ettoday.net/news/hot-news.htm"

# 設定 User-Agent（模擬瀏覽器）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 發送 GET 請求
response = requests.get(url, headers=headers)

# 確認請求成功
if response.status_code == 200:
    # 解析 HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # 使用 .block.block_1.hot-newslist 來抓取新聞列表
    news_list = soup.select(".block.block_1.hot-newslist .piece")

    # 顯示結果並存入資料庫
    for news in news_list:
        try:
            # 獲取標題與連結
            title_tag = news.select_one("h3 a")
            title = title_tag.text.strip() if title_tag else "無標題"
            title = title.replace("\u3000", " ")  # 刪除標題中的空格
            link = title_tag["href"] if title_tag else "無連結"

            # 確保 link 是完整 URL
            if not link.startswith("https"):
                link = "https://www.ettoday.net" + link

            # 獲取圖片
            img_tag = news.select_one("img")
            img = img_tag["data-original"] if img_tag and img_tag.has_attr('data-original') else "https://static.ettoday.net/style/ettoday2017/images/logo_ettoday_v4.png"

            # 存入資料庫
            if title and link:
                # 查詢是否已存在該新聞
                sql = "SELECT id FROM news WHERE platform = %s AND title = %s"
                db.cursor.execute(sql, ("ETtoday", title))
                existing_news = db.cursor.fetchone()

                if not existing_news:
                    # 插入新新聞到資料庫
                    sql = """
                    INSERT INTO news (platform, type, title, link, img) 
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    db.cursor.execute(sql, ("ETtoday", "熱門", title, link, img))
                    db.conn.commit()
                    print(f"✅ 新增新聞: {title}")
                else:
                    print(f"⚠️ 已存在: {title}")

        except Exception as e:
            print(f"❌ 發生錯誤: {e}")

else:
    print(f"❌ 請求失敗，狀態碼: {response.status_code}")

# 關閉資料庫連接
db.cursor.close()
db.conn.close()
