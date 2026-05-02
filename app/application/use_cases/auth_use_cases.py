from datetime import datetime

from fastapi import status
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.domain.enums import PerfilUsuario
from app.infrastructure.models.usuario import UsuarioModel
from app.infrastructure.repositories.usuario_repository import UsuarioRepository


class RegisterUsuarioUseCase:
    """Cadastra um novo usuário validando unicidade de e-mail e consentimento LGPD."""

    def __init__(self, db: Session) -> None:
        self._repo = UsuarioRepository(db)
        self._db = db

    def execute(
        self,
        nome: str,
        email: str,
        senha: str,
        perfil: PerfilUsuario,
        consentimento_lgpd: bool,
    ) -> UsuarioModel:
        if self._repo.buscar_por_email(email):
            raise AppException(
                status.HTTP_409_CONFLICT,
                "EMAIL_JA_CADASTRADO",
                "Já existe um usuário com este e-mail.",
            )

        model = UsuarioModel(
            nome=nome,
            email=email,
            senha_hash=hash_password(senha),
            perfil=perfil,
            consentimento_lgpd=consentimento_lgpd,
            consentimento_lgpd_em=datetime.utcnow() if consentimento_lgpd else None,
        )
        model = self._repo.criar(model)
        self._db.commit()
        self._db.refresh(model)
        return model


class LoginUsuarioUseCase:
    """Autentica o usuário e retorna par de tokens JWT (access + refresh)."""

    def __init__(self, db: Session) -> None:
        self._repo = UsuarioRepository(db)

    def execute(self, email: str, senha: str) -> dict:
        usuario = self._repo.buscar_por_email(email)
        if not usuario or not verify_password(senha, usuario.senha_hash):
            raise AppException(
                status.HTTP_401_UNAUTHORIZED,
                "CREDENCIAIS_INVALIDAS",
                "E-mail ou senha inválidos.",
            )

        if not usuario.ativo:
            raise AppException(
                status.HTTP_403_FORBIDDEN,
                "CONTA_INATIVA",
                "Esta conta foi desativada.",
            )

        payload = {"sub": str(usuario.id), "perfil": usuario.perfil.value}
        return {
            "accessToken": create_access_token(payload),
            "refreshToken": create_refresh_token(payload),
            "tokenType": "Bearer",
            "expiresIn": 3600,
            "user": {"id": usuario.id, "nome": usuario.nome, "perfil": usuario.perfil},
        }
