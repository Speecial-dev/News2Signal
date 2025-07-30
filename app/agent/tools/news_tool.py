import os
from typing import List, Dict
import httpx
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"


async def get_news(topic: str, limit: int = 20) -> List[Dict]:
    """
    Belirtilen konu hakkında en son haberleri NewsAPI'den çeker.
    - topic: Aranacak anahtar kelime (örn. "Bitcoin")
    - limit: Maksimum çekilecek haber sayısı
    Dönüş: Her bir haber için {'title', 'description', 'url', 'publishedAt'} içeren dict listesi.
    """
    params = {
        "q": topic,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": limit,
        "apiKey": NEWS_API_KEY,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    articles = []
    for a in data.get("articles", []):
        articles.append(
            {
                "title": a.get("title"),
                "description": a.get("description"),
                "url": a.get("url"),
                "publishedAt": a.get("publishedAt"),
            }
        )
    return articles
