from sqlalchemy.orm import Session

from app.domain.enums import CanalPedido, StatusPedido
from app.infrastructure.models.pedido import ItemPedidoModel, PedidoModel


class PedidoRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def criar(self, model: PedidoModel) -> PedidoModel:
        self._db.add(model)
        self._db.flush()
        self._db.refresh(model)
        return model

    def buscar_por_id(self, pedido_id: int) -> PedidoModel | None:
        return self._db.query(PedidoModel).filter(PedidoModel.id == pedido_id).first()

    def listar(
        self,
        usuario_id: int | None = None,
        unidade_id: int | None = None,
        canal_pedido: CanalPedido | None = None,
        status: StatusPedido | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> list[PedidoModel]:
        query = self._db.query(PedidoModel)
        if usuario_id is not None:
            query = query.filter(PedidoModel.usuario_id == usuario_id)
        if unidade_id is not None:
            query = query.filter(PedidoModel.unidade_id == unidade_id)
        if canal_pedido is not None:
            query = query.filter(PedidoModel.canal_pedido == canal_pedido)
        if status is not None:
            query = query.filter(PedidoModel.status == status)
        offset = (page - 1) * limit
        return query.order_by(PedidoModel.created_at.desc()).offset(offset).limit(limit).all()

    def atualizar_status(self, pedido: PedidoModel, novo_status: StatusPedido) -> PedidoModel:
        pedido.status = novo_status
        self._db.flush()
        self._db.refresh(pedido)
        return pedido
