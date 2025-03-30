# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from bs4 import BeautifulSoup
# import time

# # 目標 URL
# url = "https://news.ebc.net.tw/hot/living"

# # 啟動 Selenium WebDriver
# driver = webdriver.Chrome()
# driver.get(url)

# # 滾動加載頁面
# height = 1000
# for _ in range(3):
#     driver.execute_script(f'window.scrollTo(0, {height})')
#     time.sleep(0.5)
#     height += 1000

# # 取得 HTML 並解析
# html = driver.page_source
# soup = BeautifulSoup(html, "html.parser")

# # 找到 class 為 "tab_content" 的新聞區塊
# news_section = soup.find(class_="tab_content")

# if news_section:
#     articles = news_section.find_all("a")

#     for row in articles:
#         # 取得標題
#         title = row.get("title") or row.text.strip()

#         # 取得連結
#         link = row.get("href")
#         if not link.startswith("http"):
#             link = "https://news.ebc.net.tw" + link

#         # 取得圖片
#         img_tag = row.find("img")
#         photo = img_tag.get("data-src") or img_tag.get("src") if img_tag else "無圖片"

#         print(f"標題: {title}")
#         print(f"圖片: {photo}")
#         print(f"連結: {link}")
#         print("-" * 50)
# # 關閉資料庫
# driver.quit()


from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import db

# 目標 URL
url = "https://news.ebc.net.tw/hot/business"

# 啟動 Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 無頭模式
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)
driver.get(url)

# 滾動加載頁面
last_height = driver.execute_script("return document.body.scrollHeight")
for _ in range(3):  # 滾動 3 次
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)  # 等待新內容加載
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:  # 如果滾動後高度沒有變化，則停止滾動
        break
    last_height = new_height

# 取得 HTML 並解析
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# 找到 class 為 "tab_content" 的新聞區塊
news_section = soup.find(class_="tab_content")

if news_section:
    articles = news_section.find_all("a")

    for row in articles:
        try:
            # 取得標題
            title = row.get("title") or row.text.strip()
            if not title:
                continue  # 跳過無標題的新聞

            # 取得連結
            link = row.get("href")
            if not link or link == "#":
                continue
            if not link.startswith("http"):
                link = "https://news.ebc.net.tw" + link

            # 取得圖片
            img_tag = row.find("img")
            photo = img_tag["data-src"] if img_tag and img_tag.has_attr("data-src") else (
                img_tag["src"] if img_tag and img_tag.has_attr("src") else "https://www.ebc.net.tw/default.jpg"
            )

            # 檢查新聞是否已存在
            sql = "SELECT id FROM news WHERE platform = %s AND title = %s"
            db.cursor.execute(sql, ("EBC", title))
            existing_news = db.cursor.fetchone()

            if not existing_news:
                # 插入新聞到資料庫
                sql = """
                INSERT INTO news (platform, type, title, link, img) 
                VALUES (%s, %s, %s, %s, %s)
                """
                db.cursor.execute(sql, ("EBC", "科技", title, link, photo))
                db.conn.commit()
                print(f"✅ 新增新聞: {title}")
            else:
                print(f"⚠️ 已存在: {title}")

        except Exception as e:
            print(f"❌ 發生錯誤: {e}")

# 關閉 Selenium 瀏覽器
driver.quit()

# 關閉資料庫連線
db.cursor.close()
db.conn.close()