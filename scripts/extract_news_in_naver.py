import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import os
import time
from urllib.parse import urljoin

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

def get_naver_article_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # 여러 유형 시도
        candidates = [
            soup.find("div", id="dic_area"),
            soup.find("div", class_="newsct_article _article_body"),
            soup.find("div", id="newsEndContents"),
        ]

        for content_div in candidates:
            if content_div:
                text = content_div.get_text(strip=True)
                print("[DEBUG] 본문 일부:", text[:100])
                return text

        print(f"[WARN] 본문을 찾을 수 없음: {url}")
        return None

    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        return None

def fetch_naver_top30_news(date_str=None, max_articles=30):
    if date_str is None:
        date_str = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

    url = f"https://news.naver.com/main/ranking/popularDay.naver?date={date_str}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    news_items = []
    seen_urls = set()
    boxes = soup.select("div.rankingnews_box")

    for box in boxes:
        press = box.select_one("strong.rankingnews_name").get_text(strip=True)
        articles = box.select("ul.rankingnews_list li a")
        
        for a in articles:
            if len(news_items) >= max_articles:
                break
            link = urljoin("https://news.naver.com", a['href'])
            if link in seen_urls:
                continue
            seen_urls.add(link)
            
            title = a.get_text(strip=True)
            print("link: " + link)
            content = get_naver_article_content(link)

            news_items.append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "press": press,
                "title": title,
                "url": link,
                "content": content
            })

            time.sleep(0.5)

    df = pd.DataFrame(news_items)
    return df

if __name__ == "__main__":
    # today = datetime.now().strftime("%Y-%m-%d")
    today = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    df = fetch_naver_top30_news()
    print(df.head())

    df.to_csv(
        os.path.join(DATA_DIR, f"naver_top30_news_{today}.csv"),
        index=False, 
        encoding="utf-8-sig"
        )