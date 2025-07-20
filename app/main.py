from fastapi import FastAPI
from app.api.routes import router
import uvicorn

app = FastAPI(
    title="FinAgent - AI Powered Trading System",
    description="Agent tabanlı finansal analiz ve alım-satım otomasyonu",
    version="0.1.0"
)

# Tüm route'ları kaydet
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
