from sqlalchemy import Column, Integer, String
from backend.utils.db import Base  # Base'i db.py'de tanımlayacağız


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
