import uuid
from main.database import Base
from sqlalchemy import Column, Integer, String, Boolean, func, DateTime, ForeignKey, Table, Enum as SQLAEnum
from cryptography.fernet import Fernet

from sqlalchemy.orm import relationship, backref, mapped_column



class User(Base):
    __tablename__ = "users"
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    password = Column(String(500), nullable=False)
    role = Column(String(10), default="user", nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default="user")
    tokens = relationship("UserToken", back_populates="user")

    @property
    def get_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def get_context_string(self, context: str) -> bytes:
        from main import settings
        return f"{context}{self.password[-6]}{self.updated_at.strftime('%m%d%Y%H%M%S')}".encode()


class UserToken(Base):
    __tablename__ = "user_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(ForeignKey("users.id"))
    access_token = Column(String(250), nullable=True, index=True, default=None)
    refresh_token = Column(String(250), nullable=True, index=True,  default=None)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    user = relationship("User", back_populates="tokens")
