from fastapi import APIRouter
from app.models.request_models import AgentRequest
from app.agent.agent_runner import run_agent

router = APIRouter()

@router.post("/run-agent")
async def run_agent_route(request: AgentRequest):
    """
    Haberleri al, analiz et, karar ver ve gerekirse işlem yap.
    """
    result = await run_agent(request.topic, request.mode)
    return result
