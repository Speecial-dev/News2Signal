import os
from typing import List, Dict
from dotenv import load_dotenv
import httpx  # Eğer dış bir servis kullanacaksan

load_dotenv()

# ———— OPTION A: Local Python Model ————
# from your_sentiment_pkg import load_model, predict
# MODEL_PATH = os.getenv("SENTIMENT_MODEL_PATH", "models/sentiment.bin")
# model = load_model(MODEL_PATH)

# ———— OPTION B: Remote REST API ————
# SENTIMENT_API_URL = os.getenv("SENTIMENT_API_URL", "http://localhost:5000/analyze")


# app/agent/tools/sentiment_tool.py

import re
from typing import List, Dict


async def analyze_sentiments(news_items: List[Dict]) -> List[Dict]:
    """
    Gerçek sentiment analizi: haber içeriğine göre duygu skoru hesaplar.
    """
    results = []
    
    # Finansal pozitif/negatif kelimeler
    positive_words = [
        'yükseldi', 'arttı', 'büyüdü', 'kazanç', 'profit', 'gain', 'rise', 'up', 'positive',
        'olumlu', 'iyi', 'güçlü', 'başarılı', 'rekor', 'record', 'high', 'peak', 'bullish',
        'satın al', 'buy', 'yükseliş', 'rally', 'momentum', 'güven', 'confidence', 'optimist',
        'büyüme', 'growth', 'revenue', 'gelir', 'kazanç', 'earnings', 'beat', 'üstün'
    ]
    
    negative_words = [
        'düştü', 'azaldı', 'kayıp', 'loss', 'drop', 'down', 'negative', 'olumsuz', 'kötü',
        'zayıf', 'başarısız', 'düşüş', 'crash', 'bearish', 'sat', 'sell', 'panik', 'panic',
        'korku', 'fear', 'risk', 'tehlike', 'düşük', 'low', 'minimum', 'kayıp', 'loss',
        'zarar', 'damage', 'problem', 'sorun', 'kriz', 'crisis', 'iflas', 'bankruptcy'
    ]
    
    for item in news_items:
        # Haber metnini birleştir
        text = ""
        if item.get('title'):
            text += item['title'] + " "
        if item.get('description'):
            text += item['description'] + " "
        
        text = text.lower()
        
        # Pozitif ve negatif kelime sayısını hesapla
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        # Sentiment skoru hesapla
        total_words = len(text.split())
        if total_words > 0:
            positive_ratio = positive_count / total_words
            negative_ratio = negative_count / total_words
            
            # Skor hesaplama (0.0 - 1.0 arası)
            if positive_count > negative_count:
                score = 0.5 + (positive_ratio - negative_ratio) * 2
                score = min(score, 1.0)
            elif negative_count > positive_count:
                score = 0.5 - (negative_ratio - positive_ratio) * 2
                score = max(score, 0.0)
            else:
                score = 0.5  # Nötr
        else:
            score = 0.5
        
        # Label belirle
        if score >= 0.6:
            label = "positive"
        elif score <= 0.4:
            label = "negative"
        else:
            label = "neutral"
        
        # Detaylı analiz bilgisi
        analysis_info = {
            "positive_words_found": positive_count,
            "negative_words_found": negative_count,
            "total_words": total_words,
            "positive_ratio": positive_ratio if total_words > 0 else 0,
            "negative_ratio": negative_ratio if total_words > 0 else 0
        }
        
        results.append({
            **item, 
            "sentiment_score": round(score, 3), 
            "sentiment_label": label,
            "analysis_details": analysis_info
        })
    
    return results
