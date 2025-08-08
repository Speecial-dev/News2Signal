from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from backend.models.user import User
from backend.utils.db import get_db
from pydantic import BaseModel

router = APIRouter()


class RegisterRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = bcrypt.hash(request.password)
    user = User(email=request.email, password_hash=hashed_pw)
    db.add(user)
    db.commit()
    return {"message": "Registered successfully"}
