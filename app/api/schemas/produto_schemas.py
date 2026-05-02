from pydantic import BaseModel, Field


class UnidadeCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    endereco: str = Field(min_length=5, max_length=300)


class UnidadeUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=150)
    endereco: str | None = Field(default=None, min_length=5, max_length=300)
    ativa: bool | None = None


class UnidadeResponse(BaseModel):
    id: int
    nome: str
    endereco: str
    ativa: bool

    model_config = {"from_attributes": True}


class ProdutoCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    descricao: str = Field(default="", max_length=500)
    preco: float = Field(gt=0)
    categoria: str = Field(min_length=2, max_length=100)


class ProdutoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=150)
    descricao: str | None = Field(default=None, max_length=500)
    preco: float | None = Field(default=None, gt=0)
    categoria: str | None = Field(default=None, min_length=2, max_length=100)
    ativo: bool | None = None


class ProdutoResponse(BaseModel):
    id: int
    nome: str
    descricao: str
    preco: float
    categoria: str
    ativo: bool

    model_config = {"from_attributes": True}


class AssociarUnidadeRequest(BaseModel):
    unidade_id: int
