from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import TipoMovimentacaoEstoque
from app.infrastructure.database import Base


class EstoqueModel(Base):
    __tablename__ = "estoque"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    produto_id: Mapped[int] = mapped_column(Integer, ForeignKey("produtos.id"), nullable=False)
    unidade_id: Mapped[int] = mapped_column(Integer, ForeignKey("unidades.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class MovimentacaoEstoqueModel(Base):
    __tablename__ = "movimentacao_estoque"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    estoque_id: Mapped[int] = mapped_column(Integer, ForeignKey("estoque.id"), nullable=False)
    tipo: Mapped[TipoMovimentacaoEstoque] = mapped_column(
        Enum(TipoMovimentacaoEstoque), nullable=False
    )
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    observacao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
