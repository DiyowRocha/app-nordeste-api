"""
Cenários de teste — Estoque
T13: Consultar estoque por unidade (positivo)
T14: Movimentar estoque — entrada (positivo)
T15: Saída maior que saldo → 409 (negativo)
"""
from app.infrastructure.models.estoque import EstoqueModel
from app.infrastructure.models.produto import ProdutoModel, produto_unidade
from app.infrastructure.models.unidade import UnidadeModel
from tests.conftest import auth_header, criar_usuario_e_login


def _seed(db):
    unidade = UnidadeModel(nome="U1", endereco="Rua A")
    db.add(unidade)
    db.flush()
    produto = ProdutoModel(nome="Tapioca", descricao="", preco=10.0, categoria="Lanche")
    db.add(produto)
    db.flush()
    db.execute(produto_unidade.insert().values(produto_id=produto.id, unidade_id=unidade.id))
    estoque = EstoqueModel(produto_id=produto.id, unidade_id=unidade.id, quantidade=20)
    db.add(estoque)
    db.commit()
    return unidade.id, produto.id


def test_T13_consultar_estoque_por_unidade(client, db):
    """T13 — Consulta de estoque retorna lista com saldo correto."""
    unidade_id, produto_id = _seed(db)
    token = criar_usuario_e_login(client, perfil="GERENTE")
    resp = client.get(f"/estoque/unidades/{unidade_id}", headers=auth_header(token))
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1
    assert items[0]["quantidade"] == 20


def test_T14_entrada_estoque(client, db):
    """T14 — Entrada de estoque incrementa o saldo."""
    unidade_id, produto_id = _seed(db)
    token = criar_usuario_e_login(client, perfil="GERENTE")
    resp = client.post("/estoque/movimentar", json={
        "produto_id": produto_id,
        "unidade_id": unidade_id,
        "tipo": "ENTRADA",
        "quantidade": 10,
    }, headers=auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["quantidade"] == 30


def test_T15_saida_maior_que_saldo_retorna_409(client, db):
    """T15 — Saída de estoque maior que saldo retorna 409."""
    unidade_id, produto_id = _seed(db)
    token = criar_usuario_e_login(client, perfil="GERENTE")
    resp = client.post("/estoque/movimentar", json={
        "produto_id": produto_id,
        "unidade_id": unidade_id,
        "tipo": "SAIDA",
        "quantidade": 999,
    }, headers=auth_header(token))
    assert resp.status_code == 409
    assert resp.json()["error"] == "ESTOQUE_INSUFICIENTE"
