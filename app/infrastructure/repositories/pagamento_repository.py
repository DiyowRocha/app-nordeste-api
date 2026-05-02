from sqlalchemy.orm import Session

from app.infrastructure.models.pagamento import PagamentoModel


class PagamentoRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def criar(self, model: PagamentoModel) -> PagamentoModel:
        self._db.add(model)
        self._db.flush()
        self._db.refresh(model)
        return model

    def buscar_por_pedido(self, pedido_id: int) -> PagamentoModel | None:
        return (
            self._db.query(PagamentoModel)
            .filter(PagamentoModel.pedido_id == pedido_id)
            .first()
        )

    def atualizar(self, model: PagamentoModel) -> PagamentoModel:
        self._db.flush()
        self._db.refresh(model)
        return model
