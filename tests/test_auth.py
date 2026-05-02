"""
Cenários de teste — Auth e Usuários
T01: Login válido                 (positivo)
T02: Login sem token → 401        (negativo)
T03: Token inválido → 401         (negativo)
T04: Cadastro duplicado → 409     (negativo)
T05: Cadastro válido → 201        (positivo)
"""
from tests.conftest import auth_header, criar_usuario_e_login


def test_T01_login_valido(client):
    """T01 — Login válido retorna accessToken e dados do usuário."""
    client.post("/usuarios/", json={
        "nome": "Ana",
        "email": "ana@t.com",
        "senha": "Senha@123",
        "perfil": "CLIENTE",
        "consentimento_lgpd": True,
    })
    resp = client.post("/auth/login", json={"email": "ana@t.com", "senha": "Senha@123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "accessToken" in data
    assert data["user"]["perfil"] == "CLIENTE"


def test_T02_acesso_sem_token_retorna_401(client):
    """T02 — Acesso a endpoint protegido sem token retorna 401."""
    resp = client.get("/pedidos/")
    assert resp.status_code == 401


def test_T03_token_invalido_retorna_401(client):
    """T03 — Token inválido retorna 401."""
    resp = client.get("/pedidos/", headers={"Authorization": "Bearer token_falso"})
    assert resp.status_code == 401


def test_T04_cadastro_email_duplicado_retorna_409(client):
    """T04 — Cadastro com e-mail já existente retorna 409."""
    payload = {"nome": "Xpto", "email": "dup@t.com", "senha": "Senha@123", "perfil": "CLIENTE", "consentimento_lgpd": True}
    client.post("/usuarios/", json=payload)
    resp = client.post("/usuarios/", json=payload)
    assert resp.status_code == 409
    assert resp.json()["error"] == "EMAIL_JA_CADASTRADO"


def test_T05_cadastro_valido_retorna_201(client):
    """T05 — Cadastro com dados válidos retorna 201 e dados do usuário."""
    resp = client.post("/usuarios/", json={
        "nome": "Carlos",
        "email": "carlos@t.com",
        "senha": "Senha@123",
        "perfil": "CLIENTE",
        "consentimento_lgpd": True,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "carlos@t.com"
    assert "senha" not in data
    assert "senha_hash" not in data


def test_perfil_retorna_dados_usuario_logado(client):
    """GET /usuarios/me retorna dados corretos sem expor senha."""
    token = criar_usuario_e_login(client, "me@t.com", "Senha@123")
    resp = client.get("/usuarios/me", headers=auth_header(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "me@t.com"
    assert "senha_hash" not in data
