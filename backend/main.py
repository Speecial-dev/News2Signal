# backend/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

# *** TEK bir import tarzı seç ***
# Eğer projeyi repo kökünden "uvicorn backend.main:app" ile çalıştırıyorsan:
from backend.db.base import Base
from backend.db.session import engine
from backend.api.routes import router as api_router

# Eğer projeyi "cd backend && uvicorn main:app" ile çalıştırıyorsan
# üstteki 3 satırı yorumla, bunun yerine şunları kullan:
# from db.base import Base
# from db.session import engine
# from api.routes import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB tabloları (Alembic yoksa)
    Base.metadata.create_all(bind=engine)
    # Basit bağlantı kontrolü
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        # İstersen burada logla ya da retry mekanizması koy
        pass
    yield
    # Kapanışta yapılacak işler varsa buraya


app = FastAPI(title="News2Signal Backend", lifespan=lifespan)

# CORS - frontend portlarını ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "Backend running"}
