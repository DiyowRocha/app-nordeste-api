from fastapi import status
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.core.logging import AuditLogger
from app.domain.enums import TipoFidelidadeMovimentacao
from app.infrastructure.models.fidelidade import FidelidadePontosModel
from app.infrastructure.repositories.fidelidade_repository import FidelidadeRepository


class ResgatarPontosUseCase:
    """Resgata pontos de fidelidade do usuário, validando saldo disponível."""

    def __init__(self, db: Session) -> None:
        self._repo = FidelidadeRepository(db)
        self._db = db
        self._audit = AuditLogger(db)

    def execute(self, usuario_id: int, pontos: int) -> dict:
        saldo_atual = self._repo.saldo(usuario_id)
        if saldo_atual < pontos:
            raise AppException(
                status.HTTP_409_CONFLICT,
                "SALDO_INSUFICIENTE",
                f"Saldo de pontos insuficiente. Disponível: {saldo_atual}.",
                details=[{"field": "pontos", "issue": f"Disponível: {saldo_atual}"}],
            )

        self._repo.registrar(
            FidelidadePontosModel(
                usuario_id=usuario_id,
                pontos=pontos,
                tipo=TipoFidelidadeMovimentacao.RESGATE,
            )
        )

        self._audit.log(
            acao="RESGATAR_PONTOS",
            recurso="fidelidade",
            usuario_id=usuario_id,
            detalhes={"pontos_resgatados": pontos, "saldo_anterior": saldo_atual},
        )

        self._db.commit()
        return {"saldo_anterior": saldo_atual, "pontos_resgatados": pontos, "saldo_atual": saldo_atual - pontos}
