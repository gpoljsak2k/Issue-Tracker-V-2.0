from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "detail": str(exc.detail),
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0] if exc.errors() else None

    if first_error:
        location = " -> ".join(str(part) for part in first_error.get("loc", []))
        message = first_error.get("msg", "Invalid request")
        detail = f"{location}: {message}"
    else:
        detail = "Invalid request"

    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "detail": detail,
        },
    )