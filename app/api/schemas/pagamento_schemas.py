from datetime import datetime

from pydantic import BaseModel

from app.domain.enums import StatusPagamento


class PagamentoResponse(BaseModel):
    id: int
    pedidoId: int
    formaPagamento: str
    status: StatusPagamento
    valor: float
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, p) -> "PagamentoResponse":
        return cls(
            id=p.id,
            pedidoId=p.pedido_id,
            formaPagamento=p.forma_pagamento,
            status=p.status,
            valor=p.valor,
            createdAt=p.created_at,
        )
