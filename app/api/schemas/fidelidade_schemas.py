from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import TipoFidelidadeMovimentacao


class ResgatarPontosRequest(BaseModel):
    pontos: int = Field(gt=0)


class FidelidadeSaldoResponse(BaseModel):
    usuarioId: int
    saldo: int


class FidelidadeMovimentacaoResponse(BaseModel):
    id: int
    usuarioId: int
    pontos: int
    tipo: TipoFidelidadeMovimentacao
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, m) -> "FidelidadeMovimentacaoResponse":
        return cls(
            id=m.id,
            usuarioId=m.usuario_id,
            pontos=m.pontos,
            tipo=m.tipo,
            createdAt=m.created_at,
        )
