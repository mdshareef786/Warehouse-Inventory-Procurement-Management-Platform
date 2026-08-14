from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.custom_exceptions import AppException


async def app_exception_handler(
    request: Request,
    exc: AppException
):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": str(exc),
            "data": None
        }
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal Server Error",
            "data": None
        }
    )