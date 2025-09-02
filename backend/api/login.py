from fastapi import APIRouter

router = APIRouter()

# Örnek endpoint
@router.post("/api/login")
async def login():
    return {"message": "Login başarılı"}