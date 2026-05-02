"""
Configuração de testes com banco SQLite em memória.
Não requer MySQL ativo para rodar os testes.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# importa todos os models antes de criar as tabelas
import app.infrastructure.models.usuario  # noqa: F401
import app.infrastructure.models.unidade  # noqa: F401
import app.infrastructure.models.produto  # noqa: F401
import app.infrastructure.models.estoque  # noqa: F401
import app.infrastructure.models.pedido  # noqa: F401
import app.infrastructure.models.pagamento  # noqa: F401
import app.infrastructure.models.fidelidade  # noqa: F401
import app.infrastructure.models.audit_log  # noqa: F401

from app.infrastructure.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Cria e destrói as tabelas antes/depois de cada teste."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def criar_usuario_e_login(client, email="u@t.com", senha="Senha@123", perfil="CLIENTE"):
    client.post("/usuarios/", json={
        "nome": "Teste",
        "email": email,
        "senha": senha,
        "perfil": perfil,
        "consentimento_lgpd": True,
    })
    resp = client.post("/auth/login", json={"email": email, "senha": senha})
    return resp.json()["accessToken"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
