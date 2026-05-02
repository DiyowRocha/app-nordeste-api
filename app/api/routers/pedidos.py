from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_roles
from app.api.schemas.pedido_schemas import AtualizarStatusRequest, PedidoCreate, PedidoResponse
from app.application.use_cases.create_pedido import CriarPedidoDTO, CreatePedidoUseCase, ItemPedidoDTO
from app.application.use_cases.update_status_pedido import UpdateStatusPedidoUseCase
from app.core.exceptions import AppException
from app.domain.enums import CanalPedido, PerfilUsuario, StatusPedido
from app.infrastructure.database import get_db
from app.infrastructure.models.usuario import UsuarioModel
from app.infrastructure.repositories.pedido_repository import PedidoRepository

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def criar_pedido(
    body: PedidoCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(require_roles(
        PerfilUsuario.CLIENTE, PerfilUsuario.ATENDENTE, PerfilUsuario.ADMIN
    )),
):
    """
    Cria um pedido com itens, valida estoque, processa pagamento mock e atualiza status.
    O campo canalPedido é obrigatório.
    """
    dto = CriarPedidoDTO(
        usuario_id=current_user.id,
        unidade_id=body.unidadeId,
        canal_pedido=body.canalPedido,
        itens=[ItemPedidoDTO(produto_id=i.produtoId, quantidade=i.quantidade) for i in body.itens],
        forma_pagamento=body.formaPagamento,
        forcar_recusa_pagamento=body.forcarRecusaPagamento,
    )
    pedido = CreatePedidoUseCase(db).execute(dto)
    return PedidoResponse.from_orm(pedido)


@router.get("/", response_model=list[PedidoResponse])
def listar_pedidos(
    canalPedido: CanalPedido | None = Query(default=None),
    status_pedido: StatusPedido | None = Query(default=None, alias="status"),
    unidade_id: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    """
    Lista pedidos com filtros opcionais por canal, status e unidade.
    Clientes só visualizam seus próprios pedidos.
    """
    repo = PedidoRepository(db)
    usuario_id_filtro = (
        current_user.id if current_user.perfil == PerfilUsuario.CLIENTE else None
    )
    pedidos = repo.listar(
        usuario_id=usuario_id_filtro,
        unidade_id=unidade_id,
        canal_pedido=canalPedido,
        status=status_pedido,
        page=page,
        limit=limit,
    )
    return [PedidoResponse.from_orm(p) for p in pedidos]


@router.get("/{pedido_id}", response_model=PedidoResponse)
def buscar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    """Busca um pedido pelo ID. Clientes só acessam seus próprios pedidos."""
    repo = PedidoRepository(db)
    pedido = repo.buscar_por_id(pedido_id)
    if not pedido:
        raise AppException(status.HTTP_404_NOT_FOUND, "PEDIDO_NAO_ENCONTRADO", f"Pedido {pedido_id} não encontrado.")
    if current_user.perfil == PerfilUsuario.CLIENTE and pedido.usuario_id != current_user.id:
        raise AppException(status.HTTP_403_FORBIDDEN, "PERMISSAO_NEGADA", "Você não tem acesso a este pedido.")
    return PedidoResponse.from_orm(pedido)


@router.patch("/{pedido_id}/status", response_model=PedidoResponse)
def atualizar_status(
    pedido_id: int,
    body: AtualizarStatusRequest,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    """Atualiza o status do pedido respeitando as transições válidas e permissões por perfil."""
    pedido = UpdateStatusPedidoUseCase(db).execute(
        pedido_id=pedido_id,
        novo_status=body.status,
        perfil=current_user.perfil,
        usuario_id=current_user.id,
    )
    return PedidoResponse.from_orm(pedido)
