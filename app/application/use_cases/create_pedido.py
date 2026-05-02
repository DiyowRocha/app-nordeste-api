import json
from dataclasses import dataclass

from fastapi import status
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.core.logging import AuditLogger
from app.domain.enums import CanalPedido, StatusPagamento, StatusPedido, TipoFidelidadeMovimentacao, TipoMovimentacaoEstoque
from app.infrastructure.mock.payment_mock import processar_pagamento_mock
from app.infrastructure.models.fidelidade import FidelidadePontosModel
from app.infrastructure.models.pagamento import PagamentoModel
from app.infrastructure.models.pedido import ItemPedidoModel, PedidoModel
from app.infrastructure.repositories.estoque_repository import EstoqueRepository
from app.infrastructure.repositories.fidelidade_repository import FidelidadeRepository
from app.infrastructure.repositories.pagamento_repository import PagamentoRepository
from app.infrastructure.repositories.pedido_repository import PedidoRepository
from app.infrastructure.repositories.produto_repository import ProdutoRepository
from app.infrastructure.repositories.unidade_repository import UnidadeRepository


@dataclass
class ItemPedidoDTO:
    produto_id: int
    quantidade: int


@dataclass
class CriarPedidoDTO:
    usuario_id: int
    unidade_id: int
    canal_pedido: CanalPedido
    itens: list[ItemPedidoDTO]
    forma_pagamento: str
    forcar_recusa_pagamento: bool = False


class CreatePedidoUseCase:
    """
    Orquestra o fluxo completo de criação de pedido:
    validação de unidade → validação de produtos/estoque →
    criação do pedido → pagamento mock → atualização de status → pontos de fidelidade.
    """

    def __init__(self, db: Session) -> None:
        self._db = db
        self._pedido_repo = PedidoRepository(db)
        self._produto_repo = ProdutoRepository(db)
        self._estoque_repo = EstoqueRepository(db)
        self._pagamento_repo = PagamentoRepository(db)
        self._fidelidade_repo = FidelidadeRepository(db)
        self._unidade_repo = UnidadeRepository(db)
        self._audit = AuditLogger(db)

    def execute(self, dto: CriarPedidoDTO) -> PedidoModel:
        unidade = self._unidade_repo.buscar_por_id(dto.unidade_id)
        if not unidade or not unidade.ativa:
            raise AppException(
                status.HTTP_404_NOT_FOUND,
                "UNIDADE_NAO_ENCONTRADA",
                f"Unidade {dto.unidade_id} não encontrada ou inativa.",
            )

        itens_validados = self._validar_itens_e_estoque(dto)

        total = sum(i["quantidade"] * i["preco_unitario"] for i in itens_validados)

        pedido = PedidoModel(
            usuario_id=dto.usuario_id,
            unidade_id=dto.unidade_id,
            canal_pedido=dto.canal_pedido,
            status=StatusPedido.AGUARDANDO_PAGAMENTO,
            total=total,
        )
        pedido = self._pedido_repo.criar(pedido)

        for item_data in itens_validados:
            item = ItemPedidoModel(
                pedido_id=pedido.id,
                produto_id=item_data["produto_id"],
                quantidade=item_data["quantidade"],
                preco_unitario=item_data["preco_unitario"],
            )
            self._db.add(item)
            estoque = item_data["estoque"]
            self._estoque_repo.movimentar(
                estoque, TipoMovimentacaoEstoque.SAIDA, item_data["quantidade"]
            )

        self._db.flush()

        resposta_mock = processar_pagamento_mock(
            pedido_id=pedido.id,
            valor=total,
            forma_pagamento=dto.forma_pagamento,
            forcar_recusa=dto.forcar_recusa_pagamento,
        )

        status_pagamento = (
            StatusPagamento.APROVADO
            if resposta_mock.status == "APROVADO"
            else StatusPagamento.RECUSADO
        )

        pagamento = PagamentoModel(
            pedido_id=pedido.id,
            forma_pagamento=dto.forma_pagamento,
            status=status_pagamento,
            valor=total,
            payload_mock=json.dumps(resposta_mock.__dict__),
        )
        self._pagamento_repo.criar(pagamento)

        if status_pagamento == StatusPagamento.APROVADO:
            pedido.status = StatusPedido.EM_PREPARO
            self._acumular_pontos(dto.usuario_id, pedido.id, total)
        else:
            pedido.status = StatusPedido.PAGAMENTO_RECUSADO
            self._estornar_estoque(dto, itens_validados)

        self._db.flush()

        self._audit.log(
            acao="CRIAR_PEDIDO",
            recurso="pedidos",
            usuario_id=dto.usuario_id,
            detalhes={"pedido_id": pedido.id, "canal": dto.canal_pedido, "status_pagamento": resposta_mock.status},
        )

        self._db.commit()
        self._db.refresh(pedido)
        return pedido

    def _validar_itens_e_estoque(self, dto: CriarPedidoDTO) -> list[dict]:
        resultado = []
        erros = []
        for item_dto in dto.itens:
            produto = self._produto_repo.buscar_por_id(item_dto.produto_id)
            if not produto or not produto.ativo:
                erros.append({"field": f"itens.produto_id={item_dto.produto_id}", "issue": "Produto não encontrado."})
                continue

            estoque = self._estoque_repo.buscar_por_produto_unidade(item_dto.produto_id, dto.unidade_id)
            if not estoque or estoque.quantidade < item_dto.quantidade:
                disponivel = estoque.quantidade if estoque else 0
                erros.append({
                    "field": f"itens.produto_id={item_dto.produto_id}",
                    "issue": f"Estoque insuficiente. Disponível: {disponivel}",
                })
                continue

            resultado.append({
                "produto_id": item_dto.produto_id,
                "quantidade": item_dto.quantidade,
                "preco_unitario": produto.preco,
                "estoque": estoque,
            })

        if erros:
            raise AppException(
                status.HTTP_409_CONFLICT,
                "ESTOQUE_INSUFICIENTE",
                "Não há quantidade suficiente para um ou mais itens.",
                details=erros,
            )
        return resultado

    def _acumular_pontos(self, usuario_id: int, pedido_id: int, total: float) -> None:
        pontos = int(total)
        self._fidelidade_repo.registrar(
            FidelidadePontosModel(
                usuario_id=usuario_id,
                pontos=pontos,
                tipo=TipoFidelidadeMovimentacao.ACUMULO,
                pedido_id=pedido_id,
            )
        )

    def _estornar_estoque(self, dto: CriarPedidoDTO, itens_validados: list[dict]) -> None:
        for item_data in itens_validados:
            estoque = self._estoque_repo.buscar_por_produto_unidade(
                item_data["produto_id"], dto.unidade_id
            )
            if estoque:
                self._estoque_repo.movimentar(
                    estoque, TipoMovimentacaoEstoque.ENTRADA, item_data["quantidade"], observacao="Estorno por pagamento recusado"
                )
