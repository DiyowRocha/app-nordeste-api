from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_roles
from app.api.schemas.produto_schemas import UnidadeCreate, UnidadeResponse, UnidadeUpdate
from app.core.exceptions import AppException
from app.domain.enums import PerfilUsuario
from app.infrastructure.database import get_db
from app.infrastructure.models.unidade import UnidadeModel
from app.infrastructure.models.usuario import UsuarioModel
from app.infrastructure.repositories.unidade_repository import UnidadeRepository

router = APIRouter(prefix="/unidades", tags=["Unidades"])

_admin_gerente = require_roles(PerfilUsuario.ADMIN, PerfilUsuario.GERENTE)


@router.get("/", response_model=list[UnidadeResponse])
def listar(
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_user),
):
    """Lista todas as unidades ativas."""
    return UnidadeRepository(db).listar()


@router.get("/{unidade_id}", response_model=UnidadeResponse)
def buscar(
    unidade_id: int,
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_user),
):
    """Busca uma unidade pelo ID."""
    repo = UnidadeRepository(db)
    unidade = repo.buscar_por_id(unidade_id)
    if not unidade:
        raise AppException(status.HTTP_404_NOT_FOUND, "UNIDADE_NAO_ENCONTRADA", f"Unidade {unidade_id} não encontrada.")
    return unidade


@router.post("/", response_model=UnidadeResponse, status_code=status.HTTP_201_CREATED)
def criar(
    body: UnidadeCreate,
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(_admin_gerente),
):
    """Cria uma nova unidade (ADMIN/GERENTE)."""
    model = UnidadeModel(nome=body.nome, endereco=body.endereco)
    return UnidadeRepository(db).criar(model)


@router.put("/{unidade_id}", response_model=UnidadeResponse)
def atualizar(
    unidade_id: int,
    body: UnidadeUpdate,
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(_admin_gerente),
):
    """Atualiza dados de uma unidade (ADMIN/GERENTE)."""
    repo = UnidadeRepository(db)
    unidade = repo.buscar_por_id(unidade_id)
    if not unidade:
        raise AppException(status.HTTP_404_NOT_FOUND, "UNIDADE_NAO_ENCONTRADA", f"Unidade {unidade_id} não encontrada.")
    if body.nome is not None:
        unidade.nome = body.nome
    if body.endereco is not None:
        unidade.endereco = body.endereco
    if body.ativa is not None:
        unidade.ativa = body.ativa
    repo.atualizar(unidade)
    db.commit()
    db.refresh(unidade)
    return unidade
