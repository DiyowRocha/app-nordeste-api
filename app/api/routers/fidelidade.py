from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.schemas.fidelidade_schemas import (
    FidelidadeMovimentacaoResponse,
    FidelidadeSaldoResponse,
    ResgatarPontosRequest,
)
from app.application.use_cases.fidelidade_use_cases import ResgatarPontosUseCase
from app.core.exceptions import AppException
from app.core.logging import AuditLogger
from app.infrastructure.database import get_db
from app.infrastructure.models.usuario import UsuarioModel
from app.infrastructure.repositories.fidelidade_repository import FidelidadeRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository

router = APIRouter(prefix="/fidelidade", tags=["Fidelidade"])


@router.get("/saldo", response_model=FidelidadeSaldoResponse)
def consultar_saldo(
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    """Retorna o saldo atual de pontos de fidelidade do usuário autenticado."""
    saldo = FidelidadeRepository(db).saldo(current_user.id)
    return {"usuarioId": current_user.id, "saldo": saldo}


@router.get("/historico", response_model=list[FidelidadeMovimentacaoResponse])
def historico(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    """Lista o histórico de movimentações de pontos do usuário autenticado."""
    movs = FidelidadeRepository(db).historico(current_user.id, page, limit)
    return [FidelidadeMovimentacaoResponse.from_orm(m) for m in movs]


@router.post("/resgatar", response_model=dict, status_code=status.HTTP_200_OK)
def resgatar(
    body: ResgatarPontosRequest,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    """Resgata pontos de fidelidade, validando saldo disponível."""
    return ResgatarPontosUseCase(db).execute(current_user.id, body.pontos)


@router.post("/consentimento", response_model=dict, status_code=status.HTTP_200_OK)
def registrar_consentimento(
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    """Registra/confirma o consentimento LGPD para o programa de fidelidade."""
    if current_user.consentimento_lgpd:
        return {"mensagem": "Consentimento já registrado.", "consentimento_lgpd": True}

    repo = UsuarioRepository(db)
    current_user.consentimento_lgpd = True
    current_user.consentimento_lgpd_em = datetime.utcnow()
    repo.atualizar(current_user)

    AuditLogger(db).log(
        acao="REGISTRAR_CONSENTIMENTO_LGPD",
        recurso="fidelidade",
        usuario_id=current_user.id,
    )
    db.commit()
    return {"mensagem": "Consentimento registrado com sucesso.", "consentimento_lgpd": True}
