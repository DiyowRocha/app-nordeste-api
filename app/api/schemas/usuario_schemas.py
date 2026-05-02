from pydantic import BaseModel, EmailStr, Field

from app.domain.enums import PerfilUsuario


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=6)


class RefreshRequest(BaseModel):
    refreshToken: str


class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
    tokenType: str
    expiresIn: int
    user: dict


class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    email: EmailStr
    senha: str = Field(min_length=6)
    perfil: PerfilUsuario = PerfilUsuario.CLIENTE
    consentimento_lgpd: bool


class UsuarioUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=150)


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    perfil: PerfilUsuario
    ativo: bool
    consentimento_lgpd: bool

    model_config = {"from_attributes": True}
