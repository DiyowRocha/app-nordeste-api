from fastapi import status
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.core.logging import AuditLogger
from app.domain.enums import PerfilUsuario, StatusPedido
from app.infrastructure.models.pedido import PedidoModel
from app.infrastructure.repositories.pedido_repository import PedidoRepository


class UpdateStatusPedidoUseCase:
    """
    Atualiza o status de um pedido respeitando as transições válidas de domínio
    e as permissões de perfil do usuário.
    """

    # Mapeamento de quais perfis podem transicionar para quais status
    _PERMISSOES: dict[StatusPedido, list[PerfilUsuario]] = {
        StatusPedido.EM_PREPARO: [PerfilUsuario.ATENDENTE, PerfilUsuario.ADMIN],
        StatusPedido.PRONTO: [PerfilUsuario.COZINHA, PerfilUsuario.GERENTE, PerfilUsuario.ADMIN],
        StatusPedido.ENTREGUE: [PerfilUsuario.ATENDENTE, PerfilUsuario.GERENTE, PerfilUsuario.ADMIN],
        StatusPedido.CANCELADO: [PerfilUsuario.CLIENTE, PerfilUsuario.ATENDENTE, PerfilUsuario.GERENTE, PerfilUsuario.ADMIN],
    }

    def __init__(self, db: Session) -> None:
        self._db = db
        self._pedido_repo = PedidoRepository(db)
        self._audit = AuditLogger(db)

    def execute(
        self, pedido_id: int, novo_status: StatusPedido, perfil: PerfilUsuario, usuario_id: int
    ) -> PedidoModel:
        pedido = self._pedido_repo.buscar_por_id(pedido_id)
        if not pedido:
            raise AppException(
                status.HTTP_404_NOT_FOUND,
                "PEDIDO_NAO_ENCONTRADO",
                f"Pedido {pedido_id} não encontrado.",
            )

        perfis_permitidos = self._PERMISSOES.get(novo_status, [])
        if perfil not in perfis_permitidos:
            raise AppException(
                status.HTTP_403_FORBIDDEN,
                "TRANSICAO_NAO_PERMITIDA",
                f"Perfil {perfil} não pode definir o status {novo_status}.",
            )

        status_atual = pedido.status
        transicoes_validas = {
            StatusPedido.AGUARDANDO_PAGAMENTO: [StatusPedido.EM_PREPARO, StatusPedido.PAGAMENTO_RECUSADO, StatusPedido.CANCELADO],
            StatusPedido.PAGAMENTO_RECUSADO: [StatusPedido.CANCELADO],
            StatusPedido.EM_PREPARO: [StatusPedido.PRONTO, StatusPedido.CANCELADO],
            StatusPedido.PRONTO: [StatusPedido.ENTREGUE],
            StatusPedido.ENTREGUE: [],
            StatusPedido.CANCELADO: [],
        }
        if novo_status not in transicoes_validas.get(status_atual, []):
            raise AppException(
                status.HTTP_409_CONFLICT,
                "TRANSICAO_INVALIDA",
                f"Não é possível transicionar de {status_atual} para {novo_status}.",
            )

        pedido = self._pedido_repo.atualizar_status(pedido, novo_status)

        self._audit.log(
            acao="ATUALIZAR_STATUS_PEDIDO",
            recurso="pedidos",
            usuario_id=usuario_id,
            detalhes={"pedido_id": pedido_id, "de": status_atual, "para": novo_status},
        )
        self._db.commit()
        self._db.refresh(pedido)
        return pedido
