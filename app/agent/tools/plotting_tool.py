import os
from typing import List, Dict
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dotenv import load_dotenv

load_dotenv()

# Çıktı grafiklerinin kaydedileceği klasör
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


async def plot_sentiment_graph(topic: str, sentiments: List[Dict]) -> str:
    """
    Sentiment skoru zaman içinde nasıl değişmiş görselleştirir.
    - topic: grafik dosyasının isminde kullanılır
    - sentiments: her item içinde 'publishedAt' (ISO str) ve 'sentiment_score'
    Dönüş: kaydedilen grafik dosyasının URL/path'i
    """
    # Zaman ve skorları ayıkla
    times = [
        datetime.fromisoformat(item["publishedAt"].replace("Z", "+00:00"))
        for item in sentiments
    ]
    scores = [item["sentiment_score"] for item in sentiments]

    # Grafik oluştur
    plt.figure()
    plt.plot(times, scores)
    plt.title(f"Sentiment Trend for {topic}")
    plt.xlabel("Time")
    plt.ylabel("Sentiment Score")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%d-%m"))
    plt.gcf().autofmt_xdate()

    # Kaydet
    filename = (
        f"{topic.lower()}_sentiment_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.png"
    )
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath, bbox_inches="tight")
    plt.close()

    # Eğer FastAPI static olarak outputs dizinini sunuyorsa path yeterli,
    # yoksa dış url ile değiştirebilirsin.
    return f"/{OUTPUT_DIR}/{filename}"
