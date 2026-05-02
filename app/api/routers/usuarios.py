from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.schemas.usuario_schemas import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.application.use_cases.auth_use_cases import RegisterUsuarioUseCase
from app.core.logging import AuditLogger
from app.infrastructure.database import get_db
from app.infrastructure.models.usuario import UsuarioModel
from app.infrastructure.repositories.usuario_repository import UsuarioRepository

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def cadastrar(body: UsuarioCreate, db: Session = Depends(get_db)):
    """Cadastra um novo usuário na plataforma."""
    use_case = RegisterUsuarioUseCase(db)
    model = use_case.execute(
        nome=body.nome,
        email=body.email,
        senha=body.senha,
        perfil=body.perfil,
        consentimento_lgpd=body.consentimento_lgpd,
    )
    return model


@router.get("/me", response_model=UsuarioResponse)
def perfil(current_user: UsuarioModel = Depends(get_current_user)):
    """Retorna os dados do usuário autenticado."""
    return current_user


@router.put("/me", response_model=UsuarioResponse)
def atualizar_perfil(
    body: UsuarioUpdate,
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza dados do perfil do usuário autenticado."""
    repo = UsuarioRepository(db)
    if body.nome is not None:
        current_user.nome = body.nome
    repo.atualizar(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def deletar_conta(
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Anonimiza os dados do usuário (direito ao esquecimento LGPD)."""
    audit = AuditLogger(db)
    audit.log(
        acao="ANONIMIZAR_USUARIO",
        recurso="usuarios",
        usuario_id=current_user.id,
        detalhes={"motivo": "Solicitação do titular (LGPD Art. 18)"},
    )
    repo = UsuarioRepository(db)
    repo.anonimizar(current_user.id)
    db.commit()
