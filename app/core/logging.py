import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

logger = logging.getLogger("nordeste.audit")


class AuditLogger:
    """Registra ações sensíveis no banco e no log estruturado."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def log(
        self,
        acao: str,
        recurso: str,
        usuario_id: int | None = None,
        detalhes: dict[str, Any] | None = None,
        ip: str | None = None,
    ) -> None:
        """Persiste um registro de auditoria e emite log estruturado."""
        from app.infrastructure.models.audit_log import AuditLogModel

        entry = AuditLogModel(
            usuario_id=usuario_id,
            acao=acao,
            recurso=recurso,
            detalhes=str(detalhes or {}),
            ip=ip,
        )
        self._db.add(entry)
        self._db.flush()

        logger.info(
            "AUDIT | acao=%s recurso=%s usuario_id=%s ip=%s detalhes=%s ts=%s",
            acao,
            recurso,
            usuario_id,
            ip,
            detalhes,
            datetime.now(timezone.utc).isoformat(),
        )
