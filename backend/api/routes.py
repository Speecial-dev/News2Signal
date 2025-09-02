from fastapi import APIRouter
from backend.api.register import router as register_router
from backend.api.login import router as login_router
from backend.api.run_agent import router as agent_router
from backend.api.auth import router as auth_router

router = APIRouter()
router.include_router(register_router, prefix="/api")
router.include_router(login_router, prefix="/api")
router.include_router(agent_router, prefix="/api")
router.include_router(auth_router, prefix="/api", tags=["auth"])
