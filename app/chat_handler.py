import re
from typing import Dict, Any
from app.agent.agent_runner import run_agent
from app.ai_agent import ai_agent


class ChatHandler:
    def __init__(self):
        # Komut kalıpları ve regex'ler
        self.patterns = {
            'analyze': [
                r'(?:analiz|analiz et|kontrol et|incele)\s+(.+)',
                r'(.+?)\s+(?:analiz|analiz et|kontrol et|incele)',
                r'(.+?)\s+(?:için|hakkında)\s+(?:analiz|sentiment)',
            ],
            'sentiment': [
                r'(.+?)\s+(?:sentiment|duygu)\s+(?:analizi|analiz)',
                r'(?:sentiment|duygu)\s+(?:analizi|analiz)\s+(.+)',
            ],
            'auto_trade': [
                r'(.+?)\s+(?:otomatik|otomatik işlem|trade|alım satım)',
                r'(?:otomatik|otomatik işlem|trade|alım satım)\s+(.+)',
            ]
        }
    
    def extract_topic_and_mode(self, message: str) -> tuple[str, str]:
        """
        Kullanıcı mesajından konu ve mod bilgisini çıkarır.
        """
        message = message.lower().strip()
        
        # Selamlaşma ve genel mesajlar kontrolü
        greeting_keywords = ['selam', 'merhaba', 'hey', 'hi', 'hello', 'nasılsın', 'naber', 'teşekkür', 'thanks', 'yardım', 'help']
        if any(keyword in message for keyword in greeting_keywords):
            return None, None  # Analiz yapma
        
        # Finansal analiz anahtar kelimeleri
        analysis_keywords = ['analiz', 'sentiment', 'duygu', 'kontrol', 'incele', 'trade', 'işlem', 'alım', 'satım']
        has_analysis_intent = any(keyword in message for keyword in analysis_keywords)
        
        # Eğer analiz niyeti yoksa, sadece konu belirtilmişse de analiz yap
        crypto_stocks = ['bitcoin', 'ethereum', 'btc', 'eth', 'apple', 'tesla', 'google', 'microsoft', 'amazon', 'netflix', 'meta', 'nvidia', 'amd', 'intel']
        has_financial_topic = any(topic in message for topic in crypto_stocks)
        
        if not has_analysis_intent and not has_financial_topic:
            return None, None  # Analiz yapma
        
        # Otomatik işlem modu kontrolü
        auto_keywords = ['otomatik', 'otomatik işlem', 'trade', 'alım satım', 'işlem yap']
        is_auto = any(keyword in message for keyword in auto_keywords)
        
        # Sentiment analizi kontrolü
        sentiment_keywords = ['sentiment', 'duygu', 'duygu analizi']
        is_sentiment_only = any(keyword in message for keyword in sentiment_keywords)
        
        # Konu çıkarma
        topic = None
        
        # Analiz kalıpları
        for pattern in self.patterns['analyze']:
            match = re.search(pattern, message)
            if match:
                topic = match.group(1).strip()
                break
        
        # Sentiment kalıpları
        if not topic:
            for pattern in self.patterns['sentiment']:
                match = re.search(pattern, message)
                if match:
                    topic = match.group(1).strip()
                    break
        
        # Otomatik işlem kalıpları
        if not topic:
            for pattern in self.patterns['auto_trade']:
                match = re.search(pattern, message)
                if match:
                    topic = match.group(1).strip()
                    break
        
        # Eğer hiçbir kalıp eşleşmezse ama finansal konu varsa
        if not topic and has_financial_topic:
            # Mesajdaki finansal terimleri bul
            for financial_topic in crypto_stocks:
                if financial_topic in message:
                    topic = financial_topic
                    break
        
        # Mod belirleme
        if is_auto:
            mode = "auto"
        elif is_sentiment_only:
            mode = "manual"  # Sadece sentiment analizi
        else:
            mode = "manual"  # Varsayılan olarak manuel
        
        return topic, mode
    
    def generate_response(self, result: Dict[str, Any]) -> str:
        """
        API sonucunu kullanıcı dostu mesaja çevirir.
        """
        if 'error' in result:
            return f"Üzgünüm, bir hata oluştu: {result['error']}"
        
        response_parts = []
        
        # Karar bilgisi
        if 'decision' in result:
            decision_text = {
                'buy': 'AL',
                'sell': 'SAT', 
                'hold': 'BEKLE'
            }.get(result['decision'], result['decision'].upper())
            
            confidence = result.get('confidence', 0)
            response_parts.append(f"📊 **Karar:** {decision_text}")
            response_parts.append(f"🎯 **Güven:** %{confidence * 100:.1f}")
        
        # Grafik bilgisi
        if 'graph_url' in result:
            response_parts.append(f"📈 Sentiment grafiği oluşturuldu.")
        
        # İşlem sonucu
        if 'trade_result' in result:
            trade_status = result['trade_result'].get('status', 'unknown')
            if trade_status == 'FILLED':
                response_parts.append("✅ Otomatik işlem başarıyla gerçekleştirildi!")
            else:
                response_parts.append(f"⚠️ İşlem durumu: {trade_status}")
        
        return '\n'.join(response_parts)
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        Kullanıcı mesajını işler ve uygun yanıtı döner.
        """
        try:
            # Önce AI agent'ı dene
            ai_result = await ai_agent.process_message(message)
            
            # Eğer AI agent başarılı olduysa
            if "response" in ai_result and not "error" in ai_result:
                return {
                    "response_text": ai_result["response"],
                    "is_ai_agent": True,
                    "tools_used": ai_result.get("tools_used", []),
                    "news_data": ai_result.get("news_data", []),
                    "sentiment_data": ai_result.get("sentiment_data", [])
                }
            
            # AI agent başarısızsa, eski yöntemi kullan
            topic, mode = self.extract_topic_and_mode(message)
            
            # Eğer topic None ise, bu selamlaşma veya genel mesaj
            if topic is None:
                return {
                    "response_text": self.get_greeting_response(message),
                    "is_greeting": True
                }
            
            # Agent'ı çalıştır
            result = await run_agent(topic, mode)
            
            # Yanıtı formatla
            response_text = self.generate_response(result)
            
            return {
                **result,
                "response_text": response_text,
                "topic": topic,
                "mode": mode
            }
            
        except Exception as e:
            return {
                "error": f"İşlem sırasında bir hata oluştu: {str(e)}"
            }
    
    def get_greeting_response(self, message: str) -> str:
        """
        Selamlaşma mesajlarına uygun yanıt verir.
        """
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['selam', 'merhaba', 'hey', 'hi', 'hello']):
            return "Merhaba! 👋 Ben News2Signal, finansal analiz konusunda size yardımcı olabilirim. Hangi konu hakkında analiz yapmamı istiyorsunuz?"
        
        elif any(word in message_lower for word in ['nasılsın', 'naber', 'how are you']):
            return "İyiyim, teşekkürler! 😊 Size nasıl yardımcı olabilirim? Bitcoin, Ethereum veya başka bir konu hakkında analiz yapabilirim."
        
        elif any(word in message_lower for word in ['teşekkür', 'thanks', 'thank you']):
            return "Rica ederim! 😊 Başka bir konuda yardıma ihtiyacınız var mı?"
        
        elif any(word in message_lower for word in ['yardım', 'help', 'ne yapabilirsin']):
            return """🤖 Size şu konularda yardımcı olabilirim:
            
📊 **Finansal Analiz**: "Bitcoin analiz et", "Ethereum sentiment analizi"
📈 **Otomatik İşlem**: "Tesla için otomatik işlem yap"
📰 **Haber Analizi**: "Apple hissesi kontrol et"
🎯 **Karar Verme**: Sentiment skorlarına göre AL/SAT/BEKLE kararları

Hangi konuda analiz yapmamı istiyorsunuz?"""
        
        else:
            return "Merhaba! Ben News2Signal. Finansal analiz konusunda size yardımcı olabilirim. Hangi konu hakkında analiz yapmamı istiyorsunuz?"


# Global handler instance
chat_handler = ChatHandler() 