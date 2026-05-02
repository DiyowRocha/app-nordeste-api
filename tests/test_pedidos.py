"""
Cenários de teste — Pedidos e Pagamento Mock
T06: Pedido válido com canalPedido → 201                   (positivo)
T07: Pedido sem canalPedido → 422                          (negativo)
T08: Pedido com produto inexistente → 409                  (negativo)
T09: Pagamento mock recusado → status PAGAMENTO_RECUSADO   (positivo fluxo negativo)
T10: Acesso a pedido de outro cliente → 403                (negativo)
T11: Listar pedidos filtrando por canal                    (positivo)
T12: Atualizar status sem permissão de perfil → 403        (negativo)
"""
from app.domain.enums import StatusPedido
from app.infrastructure.models.estoque import EstoqueModel
from app.infrastructure.models.produto import ProdutoModel, produto_unidade
from app.infrastructure.models.unidade import UnidadeModel
from tests.conftest import auth_header, criar_usuario_e_login


def _seed_unidade_produto(db):
    unidade = UnidadeModel(nome="U1", endereco="Rua 1")
    db.add(unidade)
    db.flush()

    produto = ProdutoModel(nome="Baião", descricao="", preco=25.0, categoria="Prato")
    db.add(produto)
    db.flush()

    db.execute(produto_unidade.insert().values(produto_id=produto.id, unidade_id=unidade.id))

    estoque = EstoqueModel(produto_id=produto.id, unidade_id=unidade.id, quantidade=10)
    db.add(estoque)
    db.commit()
    return unidade.id, produto.id


def test_T06_criar_pedido_valido(client, db):
    """T06 — Criar pedido com itens e canalPedido válido retorna 201."""
    unidade_id, produto_id = _seed_unidade_produto(db)
    token = criar_usuario_e_login(client)
    resp = client.post("/pedidos/", json={
        "unidadeId": unidade_id,
        "canalPedido": "APP",
        "itens": [{"produtoId": produto_id, "quantidade": 2}],
        "formaPagamento": "PIX",
        "forcarRecusaPagamento": False,
    }, headers=auth_header(token))
    assert resp.status_code == 201
    data = resp.json()
    assert data["canalPedido"] == "APP"
    assert data["total"] == 50.0
    assert len(data["itens"]) == 1


def test_T07_pedido_sem_canal_retorna_422(client, db):
    """T07 — Criar pedido sem canalPedido retorna 422."""
    _, produto_id = _seed_unidade_produto(db)
    token = criar_usuario_e_login(client)
    resp = client.post("/pedidos/", json={
        "unidadeId": 1,
        "itens": [{"produtoId": produto_id, "quantidade": 1}],
        "formaPagamento": "PIX",
    }, headers=auth_header(token))
    assert resp.status_code == 422


def test_T08_pedido_produto_inexistente_retorna_409(client, db):
    """T08 — Criar pedido com produto inexistente retorna 409."""
    unidade_id, _ = _seed_unidade_produto(db)
    token = criar_usuario_e_login(client)
    resp = client.post("/pedidos/", json={
        "unidadeId": unidade_id,
        "canalPedido": "TOTEM",
        "itens": [{"produtoId": 9999, "quantidade": 1}],
        "formaPagamento": "PIX",
    }, headers=auth_header(token))
    assert resp.status_code == 409


def test_T09_pagamento_recusado_status_correto(client, db):
    """T09 — Forçar recusa de pagamento retorna pedido com status PAGAMENTO_RECUSADO."""
    unidade_id, produto_id = _seed_unidade_produto(db)
    token = criar_usuario_e_login(client)
    resp = client.post("/pedidos/", json={
        "unidadeId": unidade_id,
        "canalPedido": "WEB",
        "itens": [{"produtoId": produto_id, "quantidade": 1}],
        "formaPagamento": "CARTAO",
        "forcarRecusaPagamento": True,
    }, headers=auth_header(token))
    assert resp.status_code == 201
    assert resp.json()["status"] == StatusPedido.PAGAMENTO_RECUSADO.value


def test_T10_cliente_nao_acessa_pedido_alheio(client, db):
    """T10 — Cliente não pode acessar pedido de outro usuário (403)."""
    unidade_id, produto_id = _seed_unidade_produto(db)

    token1 = criar_usuario_e_login(client, "u1@t.com", "Senha@123")
    resp = client.post("/pedidos/", json={
        "unidadeId": unidade_id,
        "canalPedido": "APP",
        "itens": [{"produtoId": produto_id, "quantidade": 1}],
        "formaPagamento": "PIX",
    }, headers=auth_header(token1))
    pedido_id = resp.json()["pedidoId"]

    token2 = criar_usuario_e_login(client, "u2@t.com", "Senha@123")
    resp2 = client.get(f"/pedidos/{pedido_id}", headers=auth_header(token2))
    assert resp2.status_code == 403


def test_T11_filtrar_pedidos_por_canal(client, db):
    """T11 — Filtrar pedidos por canalPedido retorna apenas os do canal solicitado."""
    unidade_id, produto_id = _seed_unidade_produto(db)
    token = criar_usuario_e_login(client)

    for canal in ["APP", "TOTEM"]:
        client.post("/pedidos/", json={
            "unidadeId": unidade_id,
            "canalPedido": canal,
            "itens": [{"produtoId": produto_id, "quantidade": 1}],
            "formaPagamento": "PIX",
        }, headers=auth_header(token))

    resp = client.get("/pedidos/?canalPedido=APP", headers=auth_header(token))
    assert resp.status_code == 200
    pedidos = resp.json()
    assert all(p["canalPedido"] == "APP" for p in pedidos)


def test_T12_cozinha_nao_pode_cancelar_pedido(client, db):
    """T12 — Perfil COZINHA não pode cancelar pedido (403 por permissão de transição)."""
    unidade_id, produto_id = _seed_unidade_produto(db)

    token_admin = criar_usuario_e_login(client, "admin@t.com", "Senha@123", "ADMIN")
    resp = client.post("/pedidos/", json={
        "unidadeId": unidade_id,
        "canalPedido": "APP",
        "itens": [{"produtoId": produto_id, "quantidade": 1}],
        "formaPagamento": "PIX",
    }, headers=auth_header(token_admin))
    pedido_id = resp.json()["pedidoId"]

    token_cozinha = criar_usuario_e_login(client, "cozinha@t.com", "Senha@123", "COZINHA")
    resp2 = client.patch(
        f"/pedidos/{pedido_id}/status",
        json={"status": "CANCELADO"},
        headers=auth_header(token_cozinha),
    )
    assert resp2.status_code == 403
