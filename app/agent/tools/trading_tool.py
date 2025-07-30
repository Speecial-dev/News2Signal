import os
from typing import Dict
from dotenv import load_dotenv
from binance import AsyncClient

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
DEFAULT_AMOUNT = float(os.getenv("TRADE_AMOUNT", "0.001"))


async def execute_trade(symbol: str, decision: str, amount: float = None) -> Dict:
    """
    Binance API ile market emirleri gönderir.
    - symbol: "BTC" → "BTCUSDT" olarak çevrilir
    - decision: "buy" veya "sell"
    - amount: işlem miktarı (örn. 0.001 BTC). Yoksa DEFAULT_AMOUNT kullanır.
    Dönüş: Binance'den gelen order onayı dict'i
    """
    # Symbol formatla
    pair = f"{symbol.upper()}USDT"
    qty = amount or DEFAULT_AMOUNT

    client = await AsyncClient.create(API_KEY, SECRET_KEY)
    try:
        if decision.lower() == "buy":
            order = await client.create_order(
                symbol=pair, side="BUY", type="MARKET", quantity=qty
            )
        elif decision.lower() == "sell":
            order = await client.create_order(
                symbol=pair, side="SELL", type="MARKET", quantity=qty
            )
        else:
            return {
                "status": "no_action",
                "message": "Hold decision, no trade executed",
            }
        return {
            "status": order.get("status"),
            "orderId": order.get("orderId"),
            "executedQty": order.get("executedQty"),
            "fills": order.get("fills"),
        }
    finally:
        await client.close_connection()
