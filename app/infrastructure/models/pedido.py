from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import CanalPedido, StatusPedido
from app.infrastructure.database import Base


class PedidoModel(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    unidade_id: Mapped[int] = mapped_column(Integer, ForeignKey("unidades.id"), nullable=False)
    canal_pedido: Mapped[CanalPedido] = mapped_column(Enum(CanalPedido), nullable=False)
    status: Mapped[StatusPedido] = mapped_column(
        Enum(StatusPedido), nullable=False, default=StatusPedido.AGUARDANDO_PAGAMENTO
    )
    total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    itens: Mapped[list["ItemPedidoModel"]] = relationship(
        "ItemPedidoModel", back_populates="pedido", lazy="select"
    )


class ItemPedidoModel(Base):
    __tablename__ = "itens_pedido"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pedido_id: Mapped[int] = mapped_column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id: Mapped[int] = mapped_column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    preco_unitario: Mapped[float] = mapped_column(Float, nullable=False)

    pedido: Mapped["PedidoModel"] = relationship("PedidoModel", back_populates="itens")
