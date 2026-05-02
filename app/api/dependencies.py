from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.domain.enums import PerfilUsuario
from app.infrastructure.database import get_db
from app.infrastructure.models.usuario import UsuarioModel
from app.infrastructure.repositories.usuario_repository import UsuarioRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UsuarioModel:
    """Valida o JWT Bearer e retorna o usuário autenticado."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "TOKEN_AUSENTE",
                "message": "Token de autenticação não fornecido.",
                "details": [],
            },
        )
    token = credentials.credentials
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise ValueError("Token inválido")
        usuario_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "TOKEN_INVALIDO",
                "message": "Token de autenticação inválido ou expirado.",
                "details": [],
            },
        )

    repo = UsuarioRepository(db)
    usuario = repo.buscar_por_id(usuario_id)
    if not usuario or not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "USUARIO_NAO_ENCONTRADO",
                "message": "Usuário não encontrado ou inativo.",
                "details": [],
            },
        )
    return usuario


def require_roles(*roles: PerfilUsuario):
    """Factory de dependency que exige que o usuário tenha um dos perfis fornecidos."""

    def checker(current_user: UsuarioModel = Depends(get_current_user)) -> UsuarioModel:
        if current_user.perfil not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "PERMISSAO_NEGADA",
                    "message": f"Perfil '{current_user.perfil}' não tem permissão para este recurso.",
                    "details": [],
                },
            )
        return current_user

    return checker
