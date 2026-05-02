from pydantic import BaseModel, Field

from app.domain.enums import TipoMovimentacaoEstoque


class MovimentacaoRequest(BaseModel):
    produto_id: int
    unidade_id: int
    tipo: TipoMovimentacaoEstoque
    quantidade: int = Field(gt=0)
    observacao: str | None = Field(default=None, max_length=255)


class EstoqueResponse(BaseModel):
    id: int
    produto_id: int
    unidade_id: int
    quantidade: int

    model_config = {"from_attributes": True}
