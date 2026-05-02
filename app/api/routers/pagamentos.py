from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.schemas.pagamento_schemas import PagamentoResponse
from app.core.exceptions import AppException
from app.infrastructure.database import get_db
from app.infrastructure.models.usuario import UsuarioModel
from app.infrastructure.repositories.pagamento_repository import PagamentoRepository

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])


@router.get("/pedidos/{pedido_id}", response_model=PagamentoResponse)
def consultar_pagamento(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    """Consulta o status do pagamento de um pedido."""
    pagamento = PagamentoRepository(db).buscar_por_pedido(pedido_id)
    if not pagamento:
        raise AppException(
            status.HTTP_404_NOT_FOUND,
            "PAGAMENTO_NAO_ENCONTRADO",
            f"Nenhum pagamento encontrado para o pedido {pedido_id}.",
        )
    return PagamentoResponse.from_orm(pagamento)
