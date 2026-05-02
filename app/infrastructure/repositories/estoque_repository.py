from sqlalchemy.orm import Session

from app.domain.enums import TipoMovimentacaoEstoque
from app.infrastructure.models.estoque import EstoqueModel, MovimentacaoEstoqueModel


class EstoqueRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def buscar_por_produto_unidade(self, produto_id: int, unidade_id: int) -> EstoqueModel | None:
        return (
            self._db.query(EstoqueModel)
            .filter(
                EstoqueModel.produto_id == produto_id,
                EstoqueModel.unidade_id == unidade_id,
            )
            .first()
        )

    def listar_por_unidade(self, unidade_id: int) -> list[EstoqueModel]:
        return (
            self._db.query(EstoqueModel)
            .filter(EstoqueModel.unidade_id == unidade_id)
            .all()
        )

    def criar_ou_atualizar(self, produto_id: int, unidade_id: int, quantidade: int) -> EstoqueModel:
        estoque = self.buscar_por_produto_unidade(produto_id, unidade_id)
        if estoque:
            estoque.quantidade = quantidade
        else:
            estoque = EstoqueModel(
                produto_id=produto_id, unidade_id=unidade_id, quantidade=quantidade
            )
            self._db.add(estoque)
        self._db.flush()
        self._db.refresh(estoque)
        return estoque

    def movimentar(
        self,
        estoque: EstoqueModel,
        tipo: TipoMovimentacaoEstoque,
        quantidade: int,
        observacao: str | None = None,
    ) -> MovimentacaoEstoqueModel:
        if tipo == TipoMovimentacaoEstoque.ENTRADA:
            estoque.quantidade += quantidade
        else:
            estoque.quantidade -= quantidade

        movimentacao = MovimentacaoEstoqueModel(
            estoque_id=estoque.id,
            tipo=tipo,
            quantidade=quantidade,
            observacao=observacao,
        )
        self._db.add(movimentacao)
        self._db.flush()
        return movimentacao
