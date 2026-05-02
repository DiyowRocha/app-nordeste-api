from sqlalchemy.orm import Session

from app.domain.enums import TipoFidelidadeMovimentacao
from app.infrastructure.models.fidelidade import FidelidadePontosModel


class FidelidadeRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def saldo(self, usuario_id: int) -> int:
        """Calcula o saldo de pontos do usuário somando acúmulos e subtraindo resgates."""
        movimentos = (
            self._db.query(FidelidadePontosModel)
            .filter(FidelidadePontosModel.usuario_id == usuario_id)
            .all()
        )
        total = 0
        for m in movimentos:
            if m.tipo == TipoFidelidadeMovimentacao.ACUMULO:
                total += m.pontos
            else:
                total -= m.pontos
        return total

    def historico(self, usuario_id: int, page: int = 1, limit: int = 10) -> list[FidelidadePontosModel]:
        offset = (page - 1) * limit
        return (
            self._db.query(FidelidadePontosModel)
            .filter(FidelidadePontosModel.usuario_id == usuario_id)
            .order_by(FidelidadePontosModel.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def registrar(self, model: FidelidadePontosModel) -> FidelidadePontosModel:
        self._db.add(model)
        self._db.flush()
        self._db.refresh(model)
        return model
