from sqlalchemy import text
from sqlalchemy.orm import Session

from app.infrastructure.models.produto import ProdutoModel, produto_unidade


class ProdutoRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def listar(self, page: int = 1, limit: int = 10) -> list[ProdutoModel]:
        offset = (page - 1) * limit
        return (
            self._db.query(ProdutoModel)
            .filter(ProdutoModel.ativo.is_(True))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def listar_por_unidade(self, unidade_id: int, page: int = 1, limit: int = 10) -> list[ProdutoModel]:
        offset = (page - 1) * limit
        return (
            self._db.query(ProdutoModel)
            .join(produto_unidade, ProdutoModel.id == produto_unidade.c.produto_id)
            .filter(
                produto_unidade.c.unidade_id == unidade_id,
                ProdutoModel.ativo.is_(True),
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

    def buscar_por_id(self, produto_id: int) -> ProdutoModel | None:
        return self._db.query(ProdutoModel).filter(ProdutoModel.id == produto_id).first()

    def criar(self, model: ProdutoModel) -> ProdutoModel:
        self._db.add(model)
        self._db.flush()
        self._db.refresh(model)
        return model

    def atualizar(self, model: ProdutoModel) -> ProdutoModel:
        self._db.flush()
        self._db.refresh(model)
        return model

    def associar_unidade(self, produto_id: int, unidade_id: int) -> None:
        exists = self._db.execute(
            produto_unidade.select().where(
                produto_unidade.c.produto_id == produto_id,
                produto_unidade.c.unidade_id == unidade_id,
            )
        ).first()
        if not exists:
            self._db.execute(
                produto_unidade.insert().values(produto_id=produto_id, unidade_id=unidade_id)
            )
