from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.models.request_models import AgentRequest
from app.agent.agent_runner import run_agent
from app.chat_handler import chat_handler
import os

router = APIRouter()

# Templates dizini
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def chat_interface(request: Request):
    """
    Chatbot arayüzünü göster.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/chat")
async def chat_endpoint(request: Request):
    """
    Chatbot mesajlarını işle.
    """
    try:
        body = await request.json()
        message = body.get("message", "").strip()
        
        if not message:
            return {"error": "Mesaj boş olamaz"}
        
        # Chat handler ile mesajı işle
        result = await chat_handler.process_message(message)
        return result
        
    except Exception as e:
        return {"error": f"Mesaj işlenirken hata oluştu: {str(e)}"}


@router.post("/run-agent")
async def run_agent_route(request: AgentRequest):
    """
    Haberleri al, analiz et, karar ver ve gerekirse işlem yap.
    """
    result = await run_agent(request.topic, request.mode)
    return result
