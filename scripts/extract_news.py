import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../keys/.env")

def extract_top_headlines(max_articles=30):
    api_key = os.getenv("GNEWS_API_KEY")
    if not api_key:
        raise ValueError("GNEWS_API_KEY is not set in .env")
    
    url = "https://gnews.io/api/v4/top-headlines"
    params = {
        "lang": "ko",
        "country": "kr",
        "max": max_articles,
        "token": api_key
    }

    response = requests.get(url, params=params)
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
    return df

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    df = extract_top_headlines()
    print(df.head())
    os.makedirs("../data", exist_ok=True)
    df.to_csv(f"../data/news_{today}.csv", index=False)