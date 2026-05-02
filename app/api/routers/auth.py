from fastapi import APIRouter, Depends, Request
from jose import JWTError
from sqlalchemy.orm import Session

from app.api.schemas.usuario_schemas import LoginRequest, RefreshRequest, TokenResponse
from app.application.use_cases.auth_use_cases import LoginUsuarioUseCase
from app.core.exceptions import AppException
from app.core.security import create_access_token, decode_token
from app.infrastructure.database import get_db
from fastapi import status

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Autentica o usuário e retorna tokens JWT de acesso e refresh."""
    use_case = LoginUsuarioUseCase(db)
    return use_case.execute(body.email, body.senha)


@router.post("/refresh", response_model=dict, status_code=status.HTTP_200_OK)
def refresh_token(body: RefreshRequest):
    """Gera um novo access token a partir de um refresh token válido."""
    try:
        payload = decode_token(body.refreshToken)
        if payload.get("type") != "refresh":
            raise ValueError("Token inválido")
    except (JWTError, ValueError):
        raise AppException(
            status.HTTP_401_UNAUTHORIZED,
            "TOKEN_INVALIDO",
            "Refresh token inválido ou expirado.",
        )

    new_access = create_access_token({"sub": payload["sub"], "perfil": payload["perfil"]})
    return {"accessToken": new_access, "tokenType": "Bearer"}
