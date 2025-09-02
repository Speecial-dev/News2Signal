from fastapi import APIRouter

router = APIRouter()

# Örnek endpoint
@router.get("/api/run-agent")
async def run_agent():
    return {"message": "Agent çalıştı"}