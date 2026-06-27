from typing import cast

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def validation_error_handler(_request: Request, exc: Exception):
    validation_exc = cast(RequestValidationError, exc)
    errors = []
    for err in validation_exc.errors():
        field = " → ".join(str(loc) for loc in err["loc"])
        errors.append({"campo": field, "mensagem": err["msg"]})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Dados de entrada inválidos.", "erros": errors},
    )
