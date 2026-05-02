import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, usuarios, unidades, produtos, estoque, pedidos, pagamentos, fidelidade
from app.core.exceptions import AppException, app_exception_handler, unhandled_exception_handler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(
    title="API Raízes do Nordeste",
    description=(
        "API REST para gerenciamento da rede de lanchonetes Raízes do Nordeste. "
        "Suporta múltiplos canais (APP, TOTEM, BALCÃO, PICKUP, WEB), "
        "gestão de pedidos, estoque por unidade, fidelização e pagamento mock."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(unidades.router)
app.include_router(produtos.router)
app.include_router(estoque.router)
app.include_router(pedidos.router)
app.include_router(pagamentos.router)
app.include_router(fidelidade.router)


@app.get("/health", tags=["Health"])
def health():
    """Endpoint de health check para containers e load balancers."""
    return {"status": "ok", "service": "nordeste-api"}
