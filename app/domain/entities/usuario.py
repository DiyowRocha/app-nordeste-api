from dataclasses import dataclass, field
from datetime import datetime

from app.domain.enums import PerfilUsuario


@dataclass
class Usuario:
    """Entidade de domínio do usuário, sem dependência de ORM."""

    id: int
    nome: str
    email: str
    perfil: PerfilUsuario
    ativo: bool = True
    consentimento_lgpd: bool = False
    consentimento_lgpd_em: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
