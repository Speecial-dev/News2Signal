from fastapi import FastAPI
from backend.api.routes import router as api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS ayarı
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


# Test endpoint
@app.get("/")
def root():
    return {"message": "Backend running"}
