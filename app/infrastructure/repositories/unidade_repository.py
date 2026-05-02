from sqlalchemy.orm import Session

from app.infrastructure.models.unidade import UnidadeModel


class UnidadeRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def listar(self, apenas_ativas: bool = True) -> list[UnidadeModel]:
        query = self._db.query(UnidadeModel)
        if apenas_ativas:
            query = query.filter(UnidadeModel.ativa.is_(True))
        return query.all()

    def buscar_por_id(self, unidade_id: int) -> UnidadeModel | None:
        return self._db.query(UnidadeModel).filter(UnidadeModel.id == unidade_id).first()

    def criar(self, model: UnidadeModel) -> UnidadeModel:
        self._db.add(model)
        self._db.flush()
        self._db.refresh(model)
        return model

    def atualizar(self, model: UnidadeModel) -> UnidadeModel:
        self._db.flush()
        self._db.refresh(model)
        return model
