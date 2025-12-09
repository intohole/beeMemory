from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from typing import Any


class Base(DeclarativeBase):
    """数据库所有模型的基类"""
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        cols = {col.name: getattr(self, col.name) for col in self.__table__.columns}
        return f"{self.__class__.__name__}({', '.join([f'{k}={v!r}' for k, v in cols.items()])})"
