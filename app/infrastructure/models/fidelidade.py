from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import TipoFidelidadeMovimentacao
from app.infrastructure.database import Base


class FidelidadePontosModel(Base):
    __tablename__ = "fidelidade_pontos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    pontos: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo: Mapped[TipoFidelidadeMovimentacao] = mapped_column(
        Enum(TipoFidelidadeMovimentacao), nullable=False
    )
    pedido_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("pedidos.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
