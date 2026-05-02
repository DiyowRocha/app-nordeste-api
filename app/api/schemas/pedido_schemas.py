from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import CanalPedido, StatusPedido


class ItemPedidoRequest(BaseModel):
    produtoId: int
    quantidade: int = Field(gt=0)


class PedidoCreate(BaseModel):
    unidadeId: int
    canalPedido: CanalPedido
    itens: list[ItemPedidoRequest] = Field(min_length=1)
    formaPagamento: str = Field(min_length=2, max_length=50)
    forcarRecusaPagamento: bool = False


class AtualizarStatusRequest(BaseModel):
    status: StatusPedido


class ItemPedidoResponse(BaseModel):
    id: int
    produtoId: int
    quantidade: int
    precoUnitario: float

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_item(cls, item) -> "ItemPedidoResponse":
        return cls(
            id=item.id,
            produtoId=item.produto_id,
            quantidade=item.quantidade,
            precoUnitario=item.preco_unitario,
        )


class PedidoResponse(BaseModel):
    pedidoId: int
    usuarioId: int
    unidadeId: int
    canalPedido: CanalPedido
    status: StatusPedido
    total: float
    itens: list[ItemPedidoResponse]
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, pedido) -> "PedidoResponse":
        return cls(
            pedidoId=pedido.id,
            usuarioId=pedido.usuario_id,
            unidadeId=pedido.unidade_id,
            canalPedido=pedido.canal_pedido,
            status=pedido.status,
            total=pedido.total,
            itens=[ItemPedidoResponse.from_orm_item(i) for i in pedido.itens],
            createdAt=pedido.created_at,
        )
