import random
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class RespostaPagamentoMock:
    """Representa a resposta simulada de um gateway de pagamento externo."""

    transaction_id: str
    status: str  # "APROVADO" | "RECUSADO"
    forma_pagamento: str
    valor: float
    mensagem: str
    timestamp: str
    codigo_autorizacao: str | None


def processar_pagamento_mock(
    pedido_id: int,
    valor: float,
    forma_pagamento: str,
    forcar_recusa: bool = False,
) -> RespostaPagamentoMock:
    """
    Simula o processamento de pagamento por um gateway externo.

    - 80% de aprovação por padrão (para testes realistas).
    - Pode ser forçado a recusar via parâmetro `forcar_recusa`.
    - Representa o fluxo completo: envio → resposta do gateway.
    """
    aprovado = not forcar_recusa and random.random() < 0.8

    if aprovado:
        return RespostaPagamentoMock(
            transaction_id=str(uuid4()),
            status="APROVADO",
            forma_pagamento=forma_pagamento,
            valor=valor,
            mensagem="Pagamento aprovado com sucesso.",
            timestamp=datetime.now(timezone.utc).isoformat(),
            codigo_autorizacao=f"AUTH-{random.randint(100000, 999999)}",
        )

    return RespostaPagamentoMock(
        transaction_id=str(uuid4()),
        status="RECUSADO",
        forma_pagamento=forma_pagamento,
        valor=valor,
        mensagem="Pagamento recusado pelo emissor. Verifique os dados ou tente outro meio.",
        timestamp=datetime.now(timezone.utc).isoformat(),
        codigo_autorizacao=None,
    )
