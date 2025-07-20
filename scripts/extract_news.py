import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import csv
import re

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

def extract_top_headlines(max_articles=30):
    api_key = os.getenv("GNEWS_API_KEY")
    if not api_key:
        raise ValueError("GNEWS_API_KEY is not set in .env")
    
    url = "https://gnews.io/api/v4/top-headlines"
    # url = "https://gnews.io/api/v4/search"
    params = {
        "q": "한국",
        "lang": "ko",
        "country": "kr",
        "max": max_articles,
        "token": api_key
    }

    response = requests.get(url, params=params)
    response.encoding = 'utf-8'
    response.raise_for_status()
    articles = response.json().get("articles", [])

    data = []
    for article in articles:
        data.append({
            "data": datetime.now().strftime("%Y-%m-%d"),
            "title": article.get("title"),
            "description": article.get("description"),
            "content": article.get("content"),
            "source": article.get("source", {}).get("name"),
            "url": article.get("url")
        })

    df = pd.DataFrame(data)
    # df = df[df["title"].apply(is_korean)]
    return df

def is_korean(text):
    return bool(text) and re.search(r"[가-힣]", text)

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    df = extract_top_headlines()
    print(df.head())
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(
        os.path.join(DATA_DIR, f"news_{today}.csv"), 
        index=False, 
        quoting=csv.QUOTE_ALL,
        escapechar="\\",
        encoding="utf-8")