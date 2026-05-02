"""initial migration

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-02 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column(
            "perfil",
            sa.Enum("CLIENTE", "ATENDENTE", "COZINHA", "GERENTE", "ADMIN", name="perfilusuario"),
            nullable=False,
            server_default="CLIENTE",
        ),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("consentimento_lgpd", sa.Boolean, nullable=False, server_default="0"),
        sa.Column("consentimento_lgpd_em", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_usuarios_email", "usuarios", ["email"])

    op.create_table(
        "unidades",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("endereco", sa.String(300), nullable=False),
        sa.Column("ativa", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "produtos",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("descricao", sa.String(500), nullable=False, server_default=""),
        sa.Column("preco", sa.Float, nullable=False),
        sa.Column("categoria", sa.String(100), nullable=False),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "produto_unidade",
        sa.Column("produto_id", sa.Integer, sa.ForeignKey("produtos.id"), primary_key=True),
        sa.Column("unidade_id", sa.Integer, sa.ForeignKey("unidades.id"), primary_key=True),
    )

    op.create_table(
        "estoque",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("produto_id", sa.Integer, sa.ForeignKey("produtos.id"), nullable=False),
        sa.Column("unidade_id", sa.Integer, sa.ForeignKey("unidades.id"), nullable=False),
        sa.Column("quantidade", sa.Integer, nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "movimentacao_estoque",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("estoque_id", sa.Integer, sa.ForeignKey("estoque.id"), nullable=False),
        sa.Column(
            "tipo",
            sa.Enum("ENTRADA", "SAIDA", name="tipomovimentacaoestoque"),
            nullable=False,
        ),
        sa.Column("quantidade", sa.Integer, nullable=False),
        sa.Column("observacao", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "pedidos",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("usuario_id", sa.Integer, sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("unidade_id", sa.Integer, sa.ForeignKey("unidades.id"), nullable=False),
        sa.Column(
            "canal_pedido",
            sa.Enum("APP", "TOTEM", "BALCAO", "PICKUP", "WEB", name="canalpedido"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "AGUARDANDO_PAGAMENTO",
                "PAGAMENTO_RECUSADO",
                "EM_PREPARO",
                "PRONTO",
                "ENTREGUE",
                "CANCELADO",
                name="statuspedido",
            ),
            nullable=False,
            server_default="AGUARDANDO_PAGAMENTO",
        ),
        sa.Column("total", sa.Float, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "itens_pedido",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("pedido_id", sa.Integer, sa.ForeignKey("pedidos.id"), nullable=False),
        sa.Column("produto_id", sa.Integer, sa.ForeignKey("produtos.id"), nullable=False),
        sa.Column("quantidade", sa.Integer, nullable=False),
        sa.Column("preco_unitario", sa.Float, nullable=False),
    )

    op.create_table(
        "pagamentos",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("pedido_id", sa.Integer, sa.ForeignKey("pedidos.id"), nullable=False, unique=True),
        sa.Column("forma_pagamento", sa.String(50), nullable=False),
        sa.Column(
            "status",
            sa.Enum("AGUARDANDO", "APROVADO", "RECUSADO", name="statuspagamento"),
            nullable=False,
            server_default="AGUARDANDO",
        ),
        sa.Column("valor", sa.Float, nullable=False),
        sa.Column("payload_mock", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "fidelidade_pontos",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("usuario_id", sa.Integer, sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("pontos", sa.Integer, nullable=False),
        sa.Column(
            "tipo",
            sa.Enum("ACUMULO", "RESGATE", name="tipofidelidademovimentacao"),
            nullable=False,
        ),
        sa.Column("pedido_id", sa.Integer, sa.ForeignKey("pedidos.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("usuario_id", sa.Integer, sa.ForeignKey("usuarios.id"), nullable=True),
        sa.Column("acao", sa.String(100), nullable=False),
        sa.Column("recurso", sa.String(100), nullable=False),
        sa.Column("detalhes", sa.Text, nullable=True),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("fidelidade_pontos")
    op.drop_table("pagamentos")
    op.drop_table("itens_pedido")
    op.drop_table("pedidos")
    op.drop_table("movimentacao_estoque")
    op.drop_table("estoque")
    op.drop_table("produto_unidade")
    op.drop_table("produtos")
    op.drop_table("unidades")
    op.drop_table("usuarios")
