# DER — Diagrama Entidade-Relacionamento
## Rede "Raízes do Nordeste"

```mermaid
erDiagram
    usuarios {
        int id PK
        varchar nome
        varchar email
        varchar senha_hash
        enum perfil
        boolean ativo
        boolean consentimento_lgpd
        datetime consentimento_lgpd_em
        datetime created_at
        datetime updated_at
    }

    unidades {
        int id PK
        varchar nome
        varchar endereco
        boolean ativa
        datetime created_at
    }

    produtos {
        int id PK
        varchar nome
        varchar descricao
        float preco
        varchar categoria
        boolean ativo
        datetime created_at
        datetime updated_at
    }

    produto_unidade {
        int produto_id FK
        int unidade_id FK
    }

    estoque {
        int id PK
        int produto_id FK
        int unidade_id FK
        int quantidade
        datetime updated_at
    }

    movimentacao_estoque {
        int id PK
        int estoque_id FK
        enum tipo
        int quantidade
        varchar observacao
        datetime created_at
    }

    pedidos {
        int id PK
        int usuario_id FK
        int unidade_id FK
        enum canal_pedido
        enum status
        float total
        datetime created_at
        datetime updated_at
    }

    itens_pedido {
        int id PK
        int pedido_id FK
        int produto_id FK
        int quantidade
        float preco_unitario
    }

    pagamentos {
        int id PK
        int pedido_id FK
        varchar forma_pagamento
        enum status
        float valor
        text payload_mock
        datetime created_at
        datetime updated_at
    }

    fidelidade_pontos {
        int id PK
        int usuario_id FK
        int pontos
        enum tipo
        int pedido_id FK
        datetime created_at
    }

    audit_logs {
        int id PK
        int usuario_id FK
        varchar acao
        varchar recurso
        text detalhes
        varchar ip
        datetime created_at
    }

    usuarios ||--o{ pedidos : "realiza"
    usuarios ||--o{ fidelidade_pontos : "acumula"
    usuarios ||--o{ audit_logs : "gera"
    unidades ||--o{ pedidos : "recebe"
    unidades ||--o{ estoque : "possui"
    produtos ||--o{ estoque : "tem_saldo_em"
    produtos }o--o{ unidades : "cardapio"
    produtos }o--o{ produto_unidade : "associado"
    unidades }o--o{ produto_unidade : "associado"
    pedidos ||--o{ itens_pedido : "contem"
    pedidos ||--o| pagamentos : "tem"
    pedidos ||--o{ fidelidade_pontos : "origina"
    estoque ||--o{ movimentacao_estoque : "registra"
    produtos ||--o{ itens_pedido : "incluido_em"
```

## Cardinalidades e restrições

| Relacionamento | Regra |
|---|---|
| `usuarios` → `pedidos` | Um usuário pode ter muitos pedidos |
| `unidades` → `estoque` | Cada unidade possui estoque próprio por produto |
| `produtos` ↔ `unidades` | Cardápio por unidade (N:N via `produto_unidade`) |
| `pedidos` → `pagamentos` | Cada pedido tem exatamente 1 pagamento (unique constraint) |
| `pedidos` → `itens_pedido` | Um pedido contém 1 ou mais itens |
| `estoque` → `movimentacao_estoque` | Toda entrada/saída é registrada para auditoria |
| `pedidos` → `fidelidade_pontos` | Pontos acumulados por pedido aprovado |

## ENUMs

| Tabela | Campo | Valores |
|---|---|---|
| `usuarios` | `perfil` | CLIENTE, ATENDENTE, COZINHA, GERENTE, ADMIN |
| `pedidos` | `canal_pedido` | APP, TOTEM, BALCAO, PICKUP, WEB |
| `pedidos` | `status` | AGUARDANDO_PAGAMENTO, PAGAMENTO_RECUSADO, EM_PREPARO, PRONTO, ENTREGUE, CANCELADO |
| `pagamentos` | `status` | AGUARDANDO, APROVADO, RECUSADO |
| `movimentacao_estoque` | `tipo` | ENTRADA, SAIDA |
| `fidelidade_pontos` | `tipo` | ACUMULO, RESGATE |
