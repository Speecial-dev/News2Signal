import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import BaseTool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain.tools import tool

from pydantic import BaseModel, Field
import asyncio
from langchain_community.chat_models import ChatOpenAI

load_dotenv()

# OpenAI API Key kontrolü
OPENAI_API_KEY = os.getenv("TOGETHER_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")


class NewsToolInput(BaseModel):
    topic: str = Field(
        description="Analiz edilecek finansal konu (örn: Bitcoin, Ethereum, Apple)"
    )


class SentimentToolInput(BaseModel):
    news_data: List[Dict] = Field(description="Analiz edilecek haber listesi")


class DecisionToolInput(BaseModel):
    sentiments: List[Dict] = Field(description="Sentiment analizi sonuçları")


class TradingToolInput(BaseModel):
    symbol: str = Field(description="İşlem yapılacak sembol (örn: BTC, ETH)")
    decision: str = Field(description="İşlem kararı (buy, sell, hold)")
    amount: float = Field(description="İşlem miktarı", default=0.001)


class PlottingToolInput(BaseModel):
    topic: str = Field(description="Grafik konusu")
    sentiments: List[Dict] = Field(description="Sentiment verileri")


class FinancialAgent:
    def __init__(self):
        # OpenAI LLM

        self.llm = ChatOpenAI(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",  # Önerilen Together modeli
            temperature=0.1,
            openai_api_key=os.getenv("TOGETHER_API_KEY"),
            openai_api_base="https://api.together.xyz/v1",
        )

        # Memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        # Tools
        self.tools = [
            self.news_tool,
            self.sentiment_tool,
            self.decision_tool,
            self.trading_tool,
            self.plotting_tool,
        ]

        # Agent prompt
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Sen News2Signal, gelişmiş bir finansal analiz AI agentısın. 
            
Görevin:
1. Kullanıcının finansal analiz isteklerini anla
2. Gerekli araçları kullanarak analiz yap
3. Akıllı kararlar ver ve açıkla
4. Kullanıcıya yardımcı ol

Kullanabileceğin araçlar:
- news_tool: Güncel haberleri topla
- sentiment_tool: Haberlerin duygu analizini yap
- decision_tool: Sentiment skorlarına göre karar ver
- trading_tool: Otomatik işlem yap (sadece yüksek güvenle)
- plotting_tool: Sentiment grafiği oluştur

Önemli kurallar:
- Finansal analiz isteklerinde MUTLAKA haber topla ve sentiment analizi yap
- Haber toplama ve sentiment analizi sonuçlarını detaylı açıkla
- Her haberin sentiment skorunu ve gerekçesini belirt
- Trading işlemlerini sadece yüksek güven seviyesinde yap
- Selamlaşma ve genel sohbet için araç kullanma

Örnek iş akışı:
1. Kullanıcı "Bitcoin analiz et" dediğinde
2. news_tool ile Bitcoin haberlerini topla
3. sentiment_tool ile haberlerin duygu analizini yap
4. Sonuçları detaylı açıkla
5. decision_tool ile karar ver
6. plotting_tool ile grafik oluştur

Kullanıcı mesajını analiz et ve uygun araçları kullan.""",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # Agent oluştur
        self.agent = create_openai_tools_agent(
            llm=self.llm, tools=self.tools, prompt=self.prompt
        )

        # Agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
        )

    @tool("news_tool")
    async def news_tool(self, topic: str) -> str:
        """Belirtilen konu hakkında güncel haberleri toplar."""
        from app.agent.tools.news_tool import get_news

        try:
            news_data = await get_news(topic)

            # Haberleri formatla
            formatted_news = []
            for i, news in enumerate(news_data[:5], 1):  # İlk 5 haberi göster
                formatted_news.append(f"{i}. {news.get('title', 'Başlık yok')}")
                if news.get("description"):
                    formatted_news.append(f"   {news.get('description', '')[:100]}...")
                formatted_news.append("")

            return f"📰 {topic} için {len(news_data)} haber bulundu:\n\n" + "\n".join(
                formatted_news
            )
        except Exception as e:
            return f"❌ Haber toplama hatası: {str(e)}"

    @tool("sentiment_tool")
    async def sentiment_tool(self, news_data: List[Dict]) -> str:
        """Haberlerin duygu analizini yapar."""
        from app.agent.tools.sentiment_tool import analyze_sentiments

        try:
            sentiments = await analyze_sentiments(news_data)

            # Sentiment sonuçlarını formatla
            positive_count = sum(
                1 for s in sentiments if s.get("sentiment_label") == "positive"
            )
            negative_count = sum(
                1 for s in sentiments if s.get("sentiment_label") == "negative"
            )
            neutral_count = sum(
                1 for s in sentiments if s.get("sentiment_label") == "neutral"
            )

            avg_score = (
                sum(s.get("sentiment_score", 0) for s in sentiments) / len(sentiments)
                if sentiments
                else 0
            )

            return f"""📊 Sentiment Analizi Sonuçları:
            
📈 Pozitif Haberler: {positive_count}
📉 Negatif Haberler: {negative_count}
➡️ Nötr Haberler: {neutral_count}
📊 Ortalama Sentiment Skoru: {avg_score:.3f}

Detaylı Analiz:
{chr(10).join([f"• {s.get('title', 'Başlık yok')[:50]}... - Skor: {s.get('sentiment_score', 0):.3f} ({s.get('sentiment_label', 'unknown')})" for s in sentiments[:3]])}"""
        except Exception as e:
            return f"❌ Sentiment analizi hatası: {str(e)}"

    @tool("decision_tool")
    async def decision_tool(self, sentiments: List[Dict]) -> Dict:
        """Sentiment skorlarına göre alım-satım kararı verir."""
        from app.agent.tools.decision_tool import make_trade_decision

        try:
            decision, confidence = await make_trade_decision(sentiments)
            return {
                "status": "success",
                "decision": decision,
                "confidence": confidence,
                "reasoning": self._generate_decision_reasoning(
                    sentiments, decision, confidence
                ),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @tool("trading_tool")
    async def trading_tool(
        self, symbol: str, decision: str, amount: float = 0.001
    ) -> Dict:
        """Otomatik trading işlemi yapar (sadece yüksek güven seviyesinde)."""
        from app.agent.tools.trading_tool import execute_trade

        try:
            if decision.lower() == "hold":
                return {
                    "status": "no_action",
                    "message": "Hold kararı - işlem yapılmadı",
                }

            trade_result = await execute_trade(symbol, decision, amount)
            return {"status": "success", "trade_result": trade_result}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @tool("plotting_tool")
    async def plotting_tool(self, topic: str, sentiments: List[Dict]) -> Dict:
        """Sentiment trend grafiği oluşturur."""
        from app.agent.tools.plotting_tool import plot_sentiment_graph

        try:
            graph_url = await plot_sentiment_graph(topic, sentiments)
            return {"status": "success", "graph_url": graph_url, "topic": topic}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _generate_decision_reasoning(
        self, sentiments: List[Dict], decision: str, confidence: float
    ) -> str:
        """Karar için gerekçe oluşturur."""
        if not sentiments:
            return "Haber verisi bulunamadığı için HOLD kararı verildi."

        avg_score = sum(item.get("sentiment_score", 0) for item in sentiments) / len(
            sentiments
        )
        positive_count = sum(
            1 for item in sentiments if item.get("sentiment_label") == "positive"
        )
        negative_count = sum(
            1 for item in sentiments if item.get("sentiment_label") == "negative"
        )

        reasoning = f"""
Analiz Sonuçları:
- Ortalama Sentiment Skoru: {avg_score:.2f}
- Pozitif Haber Sayısı: {positive_count}
- Negatif Haber Sayısı: {negative_count}
- Toplam Haber Sayısı: {len(sentiments)}

Karar: {decision.upper()}
Güven Seviyesi: %{confidence * 100:.1f}

Gerekçe: {self._get_decision_explanation(decision, avg_score, positive_count, negative_count)}
"""
        return reasoning

    def _get_decision_explanation(
        self, decision: str, avg_score: float, positive: int, negative: int
    ) -> str:
        """Karar için detaylı açıklama."""
        if decision == "buy":
            if positive > negative:
                return f"Pozitif haberler ({positive}) negatif haberlerden ({negative}) fazla. Ortalama sentiment skoru ({avg_score:.2f}) yüksek."
            else:
                return f"Sentiment skoru ({avg_score:.2f}) yeterince yüksek ve teknik analiz pozitif."

        elif decision == "sell":
            if negative > positive:
                return f"Negatif haberler ({negative}) pozitif haberlerden ({positive}) fazla. Ortalama sentiment skoru ({avg_score:.2f}) düşük."
            else:
                return f"Sentiment skoru ({avg_score:.2f}) düşük ve risk faktörleri yüksek."

        else:  # hold
            return f"Sentiment skoru ({avg_score:.2f}) nötr bölgede. Pozitif ({positive}) ve negatif ({negative}) haberler dengeli."

    async def process_message(self, message: str) -> Dict[str, Any]:
        """Kullanıcı mesajını AI agent ile işler."""
        try:
            # Agent'ı çalıştır
            result = await self.agent_executor.ainvoke({"input": message})

            # Haber verilerini manuel olarak topla (eğer Bitcoin ile ilgiliyse)
            news_data = []
            sentiment_data = []

            if "bitcoin" in message.lower():
                try:
                    from app.agent.tools.news_tool import get_news
                    from app.agent.tools.sentiment_tool import analyze_sentiments

                    news_data = await get_news("Bitcoin")
                    if news_data:
                        sentiment_data = await analyze_sentiments(news_data)
                except Exception as e:
                    print(f"Haber toplama hatası: {e}")

            return {
                "response": result["output"],
                "is_ai_agent": True,
                "tools_used": self._extract_tools_used(result),
                "news_data": news_data,
                "sentiment_data": sentiment_data,
            }

        except Exception as e:
            return {
                "error": f"AI Agent işlemi sırasında hata: {str(e)}",
                "is_ai_agent": True,
            }

    def _extract_tools_used(self, result: Dict) -> List[str]:
        """Kullanılan araçları çıkarır."""
        # Bu kısım LangChain'in tool usage tracking'i ile geliştirilebilir
        return ["ai_agent"]


# Global agent instance
ai_agent = FinancialAgent()
