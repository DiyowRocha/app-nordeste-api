from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_roles
from app.api.schemas.produto_schemas import AssociarUnidadeRequest, ProdutoCreate, ProdutoResponse, ProdutoUpdate
from app.core.exceptions import AppException
from app.domain.enums import PerfilUsuario
from app.infrastructure.database import get_db
from app.infrastructure.models.produto import ProdutoModel
from app.infrastructure.models.usuario import UsuarioModel
from app.infrastructure.repositories.produto_repository import ProdutoRepository

router = APIRouter(prefix="/produtos", tags=["Produtos"])

_admin_gerente = require_roles(PerfilUsuario.ADMIN, PerfilUsuario.GERENTE)


@router.get("/", response_model=list[ProdutoResponse])
def listar(
    unidade_id: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_user),
):
    """Lista produtos com paginação. Filtra por unidade se unidade_id fornecido."""
    repo = ProdutoRepository(db)
    if unidade_id is not None:
        return repo.listar_por_unidade(unidade_id, page, limit)
    return repo.listar(page, limit)


@router.get("/{produto_id}", response_model=ProdutoResponse)
def buscar(
    produto_id: int,
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(get_current_user),
):
    """Busca um produto pelo ID."""
    produto = ProdutoRepository(db).buscar_por_id(produto_id)
    if not produto:
        raise AppException(status.HTTP_404_NOT_FOUND, "PRODUTO_NAO_ENCONTRADO", f"Produto {produto_id} não encontrado.")
    return produto


@router.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar(
    body: ProdutoCreate,
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(_admin_gerente),
):
    """Cria um novo produto (ADMIN/GERENTE)."""
    model = ProdutoModel(
        nome=body.nome,
        descricao=body.descricao,
        preco=body.preco,
        categoria=body.categoria,
    )
    produto = ProdutoRepository(db).criar(model)
    db.commit()
    db.refresh(produto)
    return produto


@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar(
    produto_id: int,
    body: ProdutoUpdate,
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(_admin_gerente),
):
    """Atualiza dados de um produto (ADMIN/GERENTE)."""
    repo = ProdutoRepository(db)
    produto = repo.buscar_por_id(produto_id)
    if not produto:
        raise AppException(status.HTTP_404_NOT_FOUND, "PRODUTO_NAO_ENCONTRADO", f"Produto {produto_id} não encontrado.")
    if body.nome is not None:
        produto.nome = body.nome
    if body.descricao is not None:
        produto.descricao = body.descricao
    if body.preco is not None:
        produto.preco = body.preco
    if body.categoria is not None:
        produto.categoria = body.categoria
    if body.ativo is not None:
        produto.ativo = body.ativo
    repo.atualizar(produto)
    db.commit()
    db.refresh(produto)
    return produto


@router.post("/{produto_id}/unidades", status_code=status.HTTP_204_NO_CONTENT)
def associar_unidade(
    produto_id: int,
    body: AssociarUnidadeRequest,
    db: Session = Depends(get_db),
    _: UsuarioModel = Depends(_admin_gerente),
):
    """Associa um produto ao cardápio de uma unidade (ADMIN/GERENTE)."""
    repo = ProdutoRepository(db)
    if not repo.buscar_por_id(produto_id):
        raise AppException(status.HTTP_404_NOT_FOUND, "PRODUTO_NAO_ENCONTRADO", f"Produto {produto_id} não encontrado.")
    repo.associar_unidade(produto_id, body.unidade_id)
    db.commit()
