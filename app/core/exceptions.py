from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Exceção base da aplicação com código de status e payload padronizado."""

    def __init__(
        self,
        status_code: int,
        error: str,
        message: str,
        details: list[dict[str, str]] | None = None,
        path: str = "",
    ) -> None:
        self.status_code = status_code
        self.error = error
        self.message = message
        self.details = details or []
        self.path = path


def _error_body(
    error: str,
    message: str,
    details: list[dict[str, str]],
    path: str,
    request_id: str,
) -> dict[str, Any]:
    return {
        "error": error,
        "message": message,
        "details": details,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "path": path,
        "requestId": request_id,
    }


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handler global para AppException."""
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(
            exc.error,
            exc.message,
            exc.details,
            exc.path or str(request.url.path),
            str(uuid4()),
        ),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler global para exceções não tratadas."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_body(
            "INTERNAL_SERVER_ERROR",
            "Ocorreu um erro inesperado. Tente novamente mais tarde.",
            [],
            str(request.url.path),
            str(uuid4()),
        ),
    )
