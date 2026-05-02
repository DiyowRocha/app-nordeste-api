from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import StatusPagamento
from app.infrastructure.database import Base


class PagamentoModel(Base):
    __tablename__ = "pagamentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pedido_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pedidos.id"), nullable=False, unique=True
    )
    forma_pagamento: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[StatusPagamento] = mapped_column(
        Enum(StatusPagamento), nullable=False, default=StatusPagamento.AGUARDANDO
    )
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    payload_mock: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
