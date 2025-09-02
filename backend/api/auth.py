from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.schemas.auth import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse
from backend.db.session import get_db
from backend.db.models import User
from backend.core.security import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    # Uygulama seviyesi kontrol (erken dön geri bildirim)
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()  # DB seviyesi güvence (unique index)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    return {"message": "Kayıt başarılı!"}

@router.post("/login", response_model=LoginResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    # Kullanıcı adı/şifre ayrımı yapma → enumeration engeli
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz kimlik bilgileri")
    token = create_access_token(sub=str(user.id))
    return {"access_token": token, "token_type": "bearer"}
