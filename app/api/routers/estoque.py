from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_roles
from app.api.schemas.estoque_schemas import EstoqueResponse, MovimentacaoRequest
from app.core.exceptions import AppException
from app.core.logging import AuditLogger
from app.domain.enums import PerfilUsuario
from app.infrastructure.database import get_db
from app.infrastructure.models.usuario import UsuarioModel
from app.infrastructure.repositories.estoque_repository import EstoqueRepository

router = APIRouter(prefix="/estoque", tags=["Estoque"])

_gerente_admin = require_roles(PerfilUsuario.ADMIN, PerfilUsuario.GERENTE)


@router.get("/unidades/{unidade_id}", response_model=list[EstoqueResponse])
def consultar_por_unidade(
    unidade_id: int,
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(require_roles(
        PerfilUsuario.ADMIN, PerfilUsuario.GERENTE, PerfilUsuario.ATENDENTE
    )),
):
    """Consulta o saldo de estoque de todos os produtos de uma unidade."""
    return EstoqueRepository(db).listar_por_unidade(unidade_id)


@router.post("/movimentar", response_model=EstoqueResponse, status_code=status.HTTP_200_OK)
def movimentar(
    body: MovimentacaoRequest,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(_gerente_admin),
):
    """Registra entrada ou saída de estoque para um produto em uma unidade (ADMIN/GERENTE)."""
    repo = EstoqueRepository(db)
    estoque = repo.buscar_por_produto_unidade(body.produto_id, body.unidade_id)
    if not estoque:
        if body.tipo.value == "SAIDA":
            raise AppException(
                status.HTTP_404_NOT_FOUND,
                "ESTOQUE_NAO_ENCONTRADO",
                f"Sem registro de estoque para produto {body.produto_id} na unidade {body.unidade_id}.",
            )
        estoque = repo.criar_ou_atualizar(body.produto_id, body.unidade_id, 0)

    if body.tipo.value == "SAIDA" and estoque.quantidade < body.quantidade:
        raise AppException(
            status.HTTP_409_CONFLICT,
            "ESTOQUE_INSUFICIENTE",
            "Quantidade solicitada maior que o saldo disponível.",
            details=[{"field": "quantidade", "issue": f"Disponível: {estoque.quantidade}"}],
        )

    repo.movimentar(estoque, body.tipo, body.quantidade, body.observacao)

    AuditLogger(db).log(
        acao=f"MOVIMENTAR_ESTOQUE_{body.tipo.value}",
        recurso="estoque",
        usuario_id=current_user.id,
        detalhes={"produto_id": body.produto_id, "unidade_id": body.unidade_id, "quantidade": body.quantidade},
    )
    db.commit()
    db.refresh(estoque)
    return estoque
