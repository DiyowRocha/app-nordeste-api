"""
Script de seed: cria dados iniciais para desenvolvimento e testes.
Execute com: python seed.py
"""
from datetime import datetime

from app.core.security import hash_password
from app.infrastructure.database import SessionLocal
from app.infrastructure.models.usuario import UsuarioModel
from app.infrastructure.models.unidade import UnidadeModel
from app.infrastructure.models.produto import ProdutoModel, produto_unidade
from app.infrastructure.models.estoque import EstoqueModel
from app.domain.enums import PerfilUsuario


def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(UsuarioModel).count() > 0:
            print("Seed já aplicado. Pulando...")
            return

        admin = UsuarioModel(
            nome="Administrador",
            email="admin@nordeste.com",
            senha_hash=hash_password("Admin@123"),
            perfil=PerfilUsuario.ADMIN,
            consentimento_lgpd=True,
            consentimento_lgpd_em=datetime.utcnow(),
        )
        gerente = UsuarioModel(
            nome="Gerente Unidade 1",
            email="gerente@nordeste.com",
            senha_hash=hash_password("Gerente@123"),
            perfil=PerfilUsuario.GERENTE,
            consentimento_lgpd=True,
            consentimento_lgpd_em=datetime.utcnow(),
        )
        cliente = UsuarioModel(
            nome="Cliente Teste",
            email="cliente@nordeste.com",
            senha_hash=hash_password("Cliente@123"),
            perfil=PerfilUsuario.CLIENTE,
            consentimento_lgpd=True,
            consentimento_lgpd_em=datetime.utcnow(),
        )
        cozinha = UsuarioModel(
            nome="Cozinheiro",
            email="cozinha@nordeste.com",
            senha_hash=hash_password("Cozinha@123"),
            perfil=PerfilUsuario.COZINHA,
            consentimento_lgpd=True,
            consentimento_lgpd_em=datetime.utcnow(),
        )
        db.add_all([admin, gerente, cliente, cozinha])
        db.flush()

        unidade1 = UnidadeModel(nome="Unidade Centro", endereco="Rua do Nordeste, 100 - Centro")
        unidade2 = UnidadeModel(nome="Unidade Shopping", endereco="Av. das Nações, 500 - Shopping")
        db.add_all([unidade1, unidade2])
        db.flush()

        p1 = ProdutoModel(nome="Baião de Dois", preco=29.90, categoria="Prato Principal", descricao="Arroz com feijão de corda, queijo coalho e carne seca")
        p2 = ProdutoModel(nome="Tapioca Recheada", preco=15.90, categoria="Lanche", descricao="Tapioca com queijo e presunto")
        p3 = ProdutoModel(nome="Caldo de Cana", preco=8.90, categoria="Bebida", descricao="Caldo de cana gelado 500ml")
        p4 = ProdutoModel(nome="Carne de Sol com Macaxeira", preco=39.90, categoria="Prato Principal", descricao="Carne de sol grelhada com macaxeira cozida")
        db.add_all([p1, p2, p3, p4])
        db.flush()

        db.execute(produto_unidade.insert(), [
            {"produto_id": p1.id, "unidade_id": unidade1.id},
            {"produto_id": p2.id, "unidade_id": unidade1.id},
            {"produto_id": p3.id, "unidade_id": unidade1.id},
            {"produto_id": p4.id, "unidade_id": unidade1.id},
            {"produto_id": p1.id, "unidade_id": unidade2.id},
            {"produto_id": p2.id, "unidade_id": unidade2.id},
            {"produto_id": p3.id, "unidade_id": unidade2.id},
        ])

        estoques = [
            EstoqueModel(produto_id=p1.id, unidade_id=unidade1.id, quantidade=50),
            EstoqueModel(produto_id=p2.id, unidade_id=unidade1.id, quantidade=100),
            EstoqueModel(produto_id=p3.id, unidade_id=unidade1.id, quantidade=200),
            EstoqueModel(produto_id=p4.id, unidade_id=unidade1.id, quantidade=30),
            EstoqueModel(produto_id=p1.id, unidade_id=unidade2.id, quantidade=40),
            EstoqueModel(produto_id=p2.id, unidade_id=unidade2.id, quantidade=80),
            EstoqueModel(produto_id=p3.id, unidade_id=unidade2.id, quantidade=150),
        ]
        db.add_all(estoques)
        db.commit()
        print("Seed aplicado com sucesso!")
        print(f"  Admin: admin@nordeste.com / Admin@123")
        print(f"  Gerente: gerente@nordeste.com / Gerente@123")
        print(f"  Cliente: cliente@nordeste.com / Cliente@123")
        print(f"  Cozinha: cozinha@nordeste.com / Cozinha@123")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed()
