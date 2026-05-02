from dataclasses import dataclass, field
from datetime import datetime

from app.domain.enums import CanalPedido, StatusPedido


@dataclass
class ItemPedido:
    produto_id: int
    quantidade: int
    preco_unitario: float
    id: int | None = None


@dataclass
class Pedido:
    """Entidade de domínio do pedido com regras de transição de status."""

    usuario_id: int
    unidade_id: int
    canal_pedido: CanalPedido
    itens: list[ItemPedido] = field(default_factory=list)
    status: StatusPedido = StatusPedido.AGUARDANDO_PAGAMENTO
    total: float = 0.0
    id: int | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Transições de status permitidas por papel
    _TRANSICOES_VALIDAS: dict = field(default_factory=lambda: {
        StatusPedido.AGUARDANDO_PAGAMENTO: [StatusPedido.EM_PREPARO, StatusPedido.PAGAMENTO_RECUSADO, StatusPedido.CANCELADO],
        StatusPedido.PAGAMENTO_RECUSADO: [StatusPedido.CANCELADO],
        StatusPedido.EM_PREPARO: [StatusPedido.PRONTO, StatusPedido.CANCELADO],
        StatusPedido.PRONTO: [StatusPedido.ENTREGUE],
        StatusPedido.ENTREGUE: [],
        StatusPedido.CANCELADO: [],
    }, repr=False, compare=False)

    def pode_transicionar_para(self, novo_status: StatusPedido) -> bool:
        """Verifica se a transição de status é válida conforme regras de negócio."""
        return novo_status in self._TRANSICOES_VALIDAS.get(self.status, [])

    def calcular_total(self) -> float:
        """Recalcula o total a partir dos itens."""
        self.total = sum(i.quantidade * i.preco_unitario for i in self.itens)
        return self.total
