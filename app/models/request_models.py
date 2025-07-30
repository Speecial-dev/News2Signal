from pydantic import BaseModel
from enum import Enum


class ModeEnum(str, Enum):
    auto = "auto"
    manual = "manual"


class AgentRequest(BaseModel):
    topic: str  # Finans konusu (örn: Bitcoin, Ethereum, Apple vs.)
    mode: ModeEnum  # İşlem modu: otomatik trade mi, sadece sinyal mi?
