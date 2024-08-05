from main.database import Base
from sqlalchemy import Column, Integer, String, Boolean, func, DateTime
from cryptography.fernet import Fernet




class User(Base):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    password = Column(String(500), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    @property
    def get_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def get_context_string(self, context) -> bytes:
        from main import settings
        return f"{context}{self.password[-6]}{self.updated_at.strftime('%m%d%Y%H%M%S')}".encode()