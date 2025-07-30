from typing import List, Dict, Tuple


async def make_trade_decision(
    sentiments: List[Dict], buy_threshold: float = 0.6, sell_threshold: float = 0.4
) -> Tuple[str, float]:
    """
    Sentiment skorlarına göre işlem kararı verir.

    Args:
        sentiments: [
            {"title": ..., "sentiment_score": float, ...},
            ...
        ]
        buy_threshold: Üst eşik (≥ ise BUY)
        sell_threshold: Alt eşik (≤ ise SELL)

    Returns:
        decision: "buy", "sell" veya "hold"
        confidence: [0.0–1.0] arası güven skoru
    """
    # Boş liste kontrolü
    if not sentiments:
        return "hold", 0.0

    # Ortalama skor
    scores = [item["sentiment_score"] for item in sentiments]
    avg_score = sum(scores) / len(scores)

    # Karar mekanizması
    if avg_score >= buy_threshold:
        decision = "buy"
        confidence = avg_score
    elif avg_score <= sell_threshold:
        decision = "sell"
        confidence = 1.0 - avg_score
    else:
        decision = "hold"
        # Hold için confidence: ne kadar 0.5’e yakınsa o kadar güvenli
        confidence = 1.0 - (abs(avg_score - 0.5) * 2)

    # Yuvarlama
    return decision, round(confidence, 2)
