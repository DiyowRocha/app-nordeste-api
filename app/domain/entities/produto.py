from dataclasses import dataclass


@dataclass
class Produto:
    """Entidade de domínio do produto."""

    nome: str
    preco: float
    categoria: str
    descricao: str = ""
    ativo: bool = True
    id: int | None = None


@dataclass
class Estoque:
    """Representa o saldo de um produto em uma unidade."""

    produto_id: int
    unidade_id: int
    quantidade: int
    id: int | None = None

    def tem_saldo_para(self, quantidade_solicitada: int) -> bool:
        """Verifica se há estoque suficiente para a quantidade solicitada."""
        return self.quantidade >= quantidade_solicitada
