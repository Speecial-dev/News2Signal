from app.agent.tools.news_tool import get_news
from app.agent.tools.sentiment_tool import analyze_sentiments
from app.agent.tools.decision_tool import make_trade_decision
from app.agent.tools.trading_tool import execute_trade
from app.agent.tools.plotting_tool import plot_sentiment_graph


async def run_agent(topic: str, mode: str):
    # 1. Haberleri çek
    news_data = await get_news(topic)

    # 2. Sentiment analizini yap
    sentiments = await analyze_sentiments(news_data)

    # 3. Grafik oluştur
    graph_url = await plot_sentiment_graph(topic, sentiments)

    # 4. Karar ver (BUY, SELL, HOLD)
    decision, confidence = await make_trade_decision(sentiments)

    response = {
        "topic": topic,
        "decision": decision,
        "confidence": confidence,
        "graph_url": graph_url,
    }

    # 5. Otomatik modda işlem aç (opsiyonel)
    if mode == "auto" and confidence > 0.8:  # güven seviyesi %80 üzeri
        trade_result = await execute_trade(topic, decision)
        response["trade_result"] = trade_result

    return response
