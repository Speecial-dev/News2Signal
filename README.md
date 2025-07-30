# 🤖 News2Signal - AI Destekli Finansal Analiz Sistemi

News2Signal, haber analizi yaparak otomatik alım-satım kararları veren gelişmiş bir AI sistemi. Kullanıcı dostu chatbot arayüzü ile doğal dil komutlarıyla finansal analiz yapabilirsiniz.

## ✨ Özellikler

- **🤖 Akıllı Chatbot**: Doğal dil ile etkileşim
- **📰 Haber Analizi**: NewsAPI ile güncel haber toplama
- **💭 Sentiment Analizi**: Haberlerin duygu skorunu hesaplama
- **📊 Görselleştirme**: Sentiment trend grafikleri
- **🎯 Karar Verme**: AI destekli alım-satım kararları
- **⚡ Otomatik İşlem**: Binance API ile gerçek trading
- **🎨 Modern UI**: Responsive ve kullanıcı dostu arayüz

## 🚀 Hızlı Başlangıç

### 1. Kurulum

```bash
# Projeyi klonlayın
git clone <repository-url>
cd News2Signal

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

### 2. Çevre Değişkenleri

`.env` dosyası oluşturun:

```env
# NewsAPI (https://newsapi.org/)
NEWS_API_KEY=your_news_api_key

# Binance API (opsiyonel - otomatik trading için)
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
TRADE_AMOUNT=0.001

# Sentiment API (opsiyonel)
SENTIMENT_API_URL=http://localhost:5000/analyze
```

### 3. Çalıştırma

```bash
python -m app.main
```

Uygulama `http://localhost:8000` adresinde çalışacak.

## 💬 Kullanım

### Chatbot Komutları

Chatbot arayüzünde şu komutları kullanabilirsiniz:

```
✅ "Bitcoin analiz et"
✅ "Ethereum sentiment analizi yap"
✅ "Apple hissesi kontrol et"
✅ "Tesla için otomatik işlem yap"
✅ "Bitcoin"
✅ "Ethereum"
```

### API Endpoint'leri

#### Chatbot
- `GET /` - Chatbot arayüzü
- `POST /chat` - Chatbot mesaj işleme

#### Agent
- `POST /run-agent` - Manuel agent çalıştırma

```json
{
  "topic": "Bitcoin",
  "mode": "auto"  // veya "manual"
}
```

## 🏗️ Proje Yapısı

```
News2Signal/
├── app/
│   ├── agent/
│   │   ├── tools/
│   │   │   ├── news_tool.py      # Haber toplama
│   │   │   ├── sentiment_tool.py # Duygu analizi
│   │   │   ├── decision_tool.py  # Karar verme
│   │   │   ├── trading_tool.py   # Trading işlemleri
│   │   │   └── plotting_tool.py  # Grafik oluşturma
│   │   └── agent_runner.py       # Ana agent
│   ├── api/
│   │   └── routes.py             # API endpoint'leri
│   ├── models/
│   │   └── request_models.py     # Pydantic modelleri
│   ├── templates/
│   │   └── index.html           # Chatbot arayüzü
│   ├── chat_handler.py          # Chatbot işleme
│   └── main.py                  # FastAPI uygulaması
├── outputs/                     # Grafik çıktıları
├── requirements.txt
└── README.md
```

## 🔧 Teknik Detaylar

### Mimari

- **FastAPI**: Modern web framework
- **Async/Await**: Asenkron işlemler
- **Modüler Yapı**: Her işlev ayrı tool'larda
- **REST API**: Standart HTTP endpoint'leri

### İş Akışı

1. **Haber Toplama**: NewsAPI ile güncel haberler
2. **Sentiment Analizi**: Haberlerin duygu skorunu hesaplama
3. **Grafik Oluşturma**: Sentiment trend görselleştirme
4. **Karar Verme**: AI destekli alım-satım kararı
5. **Otomatik İşlem**: Binance API ile trading (opsiyonel)

### Güvenlik

- API anahtarları `.env` dosyasında
- Sadece yüksek güven seviyesinde otomatik işlem
- Hata yönetimi ve loglama

## 🎯 Gelecek Özellikler

- [ ] Gerçek AI sentiment analizi
- [ ] Daha fazla borsa desteği
- [ ] Portföy yönetimi
- [ ] Risk analizi
- [ ] Mobil uygulama
- [ ] Webhook entegrasyonları

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 📞 İletişim

- **Proje**: [GitHub Repository]
- **Email**: [your-email@example.com]

---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!
