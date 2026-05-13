# API Raízes do Nordeste - Projeto Final do Curso de Análise e Desenvolvimento de Sistemas

API REST para gerenciamento da rede de lanchonetes **Raízes do Nordeste**.  
Suporta múltiplos canais (APP, TOTEM, BALCÃO, PICKUP, WEB), gestão de pedidos, estoque por unidade, fidelização e pagamento mock.

## Links do projeto

| Recurso | URL |
|---|---|
| Repositório | https://github.com/DiyowRocha/app-nordeste-api |
| Swagger UI (local) | http://localhost:8000/docs |
| ReDoc (local) | http://localhost:8000/redoc |
| Coleção Postman | [`postman/nordeste-api.postman_collection.json`](postman/nordeste-api.postman_collection.json) |
| DER | [`docs/DER.md`](docs/DER.md) |

## Requisitos

| Dependência | Versão mínima |
|---|---|
| Python | 3.12 |
| MySQL | 8.0 |
| Docker + Docker Compose | opcional (recomendado) |

## Configuração de variáveis de ambiente

```bash
cp .env.example .env
# edite .env com suas credenciais
```

Variáveis obrigatórias:

| Variável | Descrição |
|---|---|
| `SECRET_KEY` | Chave secreta JWT (use `openssl rand -hex 32`) |
| `DB_HOST` | Host do MySQL |
| `DB_PORT` | Porta do MySQL (padrão `3306`) |
| `DB_USER` | Usuário do banco |
| `DB_PASSWORD` | Senha do banco |
| `DB_NAME` | Nome do banco (`nordeste_db`) |

## Opção 1 — Executar com Docker Compose (recomendado)

```bash
# Copiar variáveis de ambiente
cp .env.example .env

# Subir MySQL + API
docker-compose up --build

# A API estará disponível em: http://localhost:8000
# Swagger: http://localhost:8000/docs
```

Após os containers subirem, rode as migrations e seed:

```bash
docker-compose exec api python -m alembic upgrade head
docker-compose exec api python seed.py
```

## Opção 2 — Executar localmente

### 1. Criar e ativar virtualenv

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Criar banco de dados

```sql
CREATE DATABASE nordeste_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Executar migrations

```bash
alembic upgrade head
```

### 5. Popular banco com dados iniciais (seed)

```bash
python seed.py
```

Credenciais criadas pelo seed:

| Perfil | E-mail | Senha |
|---|---|---|
| ADMIN | admin@nordeste.com | Admin@123 |
| GERENTE | gerente@nordeste.com | Gerente@123 |
| CLIENTE | cliente@nordeste.com | Cliente@123 |
| COZINHA | cozinha@nordeste.com | Cozinha@123 |

### 6. Iniciar a API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Documentação Swagger / OpenAPI

Após iniciar a API, acesse:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health check:** http://localhost:8000/health

## Executar testes

Os testes utilizam SQLite em memória — **não requer MySQL ativo**.

```bash
# Com virtualenv ativado:
pytest tests/ -v

# Ou via .venv:
.venv/bin/python -m pytest tests/ -v
```

Resultado esperado: **16 passed**.

## Coleção Postman / Plano de Testes

A coleção está em [`postman/nordeste-api.postman_collection.json`](postman/nordeste-api.postman_collection.json).

### Como importar e executar

1. Abra o Postman e clique em **Import**
2. Selecione o arquivo `postman/nordeste-api.postman_collection.json`
3. A coleção usa variável `{{base_url}}` = `http://localhost:8000`
4. Execute na seguinte ordem para que os tokens sejam preenchidos automaticamente:
   1. **Auth / T01 — Login válido (cliente)** — salva `{{access_token}}`
   2. **Auth / Login — ADMIN** — salva `{{access_token_admin}}`
   3. **Auth / Login — Cozinha** — salva `{{access_token_cozinha}}`
   4. Demais requisições nas pastas: Usuários → Unidades → Produtos → Estoque → Pedidos → Pagamentos → Fidelidade

### Cenários cobertos

| ID | Cenário | Método | Rota | Esperado |
|---|---|---|---|---|
| T01 | Login válido | POST | /auth/login | 200 + accessToken |
| T02 | Sem token | GET | /pedidos/ | 401 |
| T03 | Token inválido | GET | /pedidos/ | 401 |
| T04 | E-mail duplicado | POST | /usuarios/ | 409 |
| T05 | Cadastro válido | POST | /usuarios/ | 201 |
| T06 | Pedido válido APP | POST | /pedidos/ | 201 |
| T07 | Pedido sem canalPedido | POST | /pedidos/ | 422 |
| T08 | Produto inexistente | POST | /pedidos/ | 409 |
| T09 | Pagamento recusado | POST | /pedidos/ | 201 + PAGAMENTO_RECUSADO |
| T11 | Filtrar por canal | GET | /pedidos/?canalPedido=APP | 200 |
| T12 | Cozinha tenta cancelar | PATCH | /pedidos/{id}/status | 403 |
| T13 | Consultar estoque | GET | /estoque/unidades/1 | 200 |
| T14 | Entrada estoque | POST | /estoque/movimentar | 200 |
| T15 | Saída > saldo | POST | /estoque/movimentar | 409 |

## Estrutura do projeto

```
app-nordeste-api/
├── app/
│   ├── api/
│   │   ├── routers/         # auth, usuarios, unidades, produtos, estoque, pedidos, pagamentos, fidelidade
│   │   ├── schemas/         # Schemas Pydantic (request/response) por módulo
│   │   └── dependencies.py  # get_current_user, require_roles
│   ├── application/
│   │   └── use_cases/       # CreatePedidoUseCase, UpdateStatusPedidoUseCase, etc.
│   ├── domain/
│   │   ├── entities/        # Entidades de domínio (sem dependência de ORM)
│   │   └── enums.py         # CanalPedido, StatusPedido, PerfilUsuario...
│   ├── infrastructure/
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── repositories/    # Repositórios por entidade
│   │   ├── mock/            # payment_mock.py (simulação de gateway)
│   │   └── database.py      # Engine, SessionLocal, get_db
│   ├── core/
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   ├── security.py      # JWT + bcrypt
│   │   ├── exceptions.py    # AppException + handlers padronizados
│   │   └── logging.py       # AuditLogger
│   └── main.py              # Entrypoint FastAPI
├── alembic/                 # Migrations
├── tests/                   # Pytest (16 cenários)
├── seed.py                  # Dados iniciais
├── .env.example
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Módulos e endpoints principais

| Módulo | Endpoints |
|---|---|
| `/auth` | POST /login, POST /refresh |
| `/usuarios` | POST /, GET /me, PUT /me, DELETE /me |
| `/unidades` | GET /, GET /{id}, POST /, PUT /{id} |
| `/produtos` | GET /, GET /{id}, POST /, PUT /{id}, POST /{id}/unidades |
| `/estoque` | GET /unidades/{id}, POST /movimentar |
| `/pedidos` | POST /, GET /, GET /{id}, PATCH /{id}/status |
| `/pagamentos` | GET /pedidos/{pedido_id} |
| `/fidelidade` | GET /saldo, GET /historico, POST /resgatar, POST /consentimento |

## Segurança e LGPD

- Senhas armazenadas com **bcrypt** via passlib — nunca expostas em responses
- Autenticação via **JWT Bearer** (access token + refresh token)
- Autorização por **roles** em cada endpoint via `Depends`
- **Logs de auditoria** em ações sensíveis: criação/cancelamento de pedido, mudança de status, movimentação de estoque, resgate de pontos
- **Consentimento LGPD** registrado no cadastro com timestamp
- `DELETE /usuarios/me` realiza **anonimização** (direito ao esquecimento, LGPD Art. 18)
- Dados sensíveis nunca retornados nas responses (`senha_hash`, payload completo de pagamento)

## Padrão de erro

Todas as respostas de erro seguem o formato:

```json
{
  "error": "NOME_DO_ERRO",
  "message": "Mensagem legível para o usuário.",
  "details": [{"field": "campo", "issue": "problema"}],
  "timestamp": "2026-05-02T11:00:00Z",
  "path": "/rota",
  "requestId": "uuid"
}
```

## Fluxo crítico — Pedido → Pagamento Mock → Status

```
POST /pedidos
  → valida unidade
  → valida produtos e estoque por unidade
  → cria pedido (AGUARDANDO_PAGAMENTO)
  → baixa estoque
  → processa pagamento mock (80% aprovação)
  → registra pagamento
  → atualiza status (EM_PREPARO | PAGAMENTO_RECUSADO)
  → acumula pontos de fidelidade (se aprovado)
  → grava audit_log
```
