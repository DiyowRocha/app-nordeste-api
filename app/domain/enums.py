from enum import Enum


class PerfilUsuario(str, Enum):
    CLIENTE = "CLIENTE"
    ATENDENTE = "ATENDENTE"
    COZINHA = "COZINHA"
    GERENTE = "GERENTE"
    ADMIN = "ADMIN"


class CanalPedido(str, Enum):
    APP = "APP"
    TOTEM = "TOTEM"
    BALCAO = "BALCAO"
    PICKUP = "PICKUP"
    WEB = "WEB"


class StatusPedido(str, Enum):
    AGUARDANDO_PAGAMENTO = "AGUARDANDO_PAGAMENTO"
    PAGAMENTO_RECUSADO = "PAGAMENTO_RECUSADO"
    EM_PREPARO = "EM_PREPARO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"


class StatusPagamento(str, Enum):
    AGUARDANDO = "AGUARDANDO"
    APROVADO = "APROVADO"
    RECUSADO = "RECUSADO"


class TipoMovimentacaoEstoque(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"


class TipoFidelidadeMovimentacao(str, Enum):
    ACUMULO = "ACUMULO"
    RESGATE = "RESGATE"
