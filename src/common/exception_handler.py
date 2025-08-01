from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from src.common.response_base_model import Result  
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from src.common.response_base_model import Result
from src.common.logger import logger  
from src.constants.constant import ERROR_CODE, ERROR_MESSAGE


async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(
        f"[DB_EXCEPTION] Path: {request.url} | Error: {str(exc)}",
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content=Result.fail(
            message=ERROR_MESSAGE.DB_ERROR + " : " + str(exc),
            errorCode=ERROR_CODE.DB_ERROR,
            meta={"path": str(request.url)}
        ).model_dump()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        f"[VALIDATION_EXCEPTION] Path: {request.url} | Errors: {exc.errors()} | Body: {exc.body}"
    )
    return JSONResponse(
        status_code=422,
        content=Result.fail(
            message=ERROR_MESSAGE.VALIDATION_ERROR + " : " + str(exc),
            errorCode=ERROR_CODE.VALIDATION_ERROR,
            meta={
                "errors": exc.errors(),
                "body": exc.body,
                "path": str(request.url)
            }
        ).model_dump()
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    logger.info(
        f"[HTTP_EXCEPTION] Path: {request.url} | Status: {exc.status_code} | Detail: {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=Result.fail(
            message=exc.detail,
            errorCode=f"HTTP_{exc.status_code}",
            meta={"path": str(request.url)}
        ).model_dump()
    )


async def global_exception_handler(request: Request, exc: Exception):
    logger.critical(
        f"[GLOBAL_EXCEPTION] Path: {request.url} | Error: {str(exc)}",
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content=Result.fail(
            message=ERROR_MESSAGE.INTERNAL_ERROR + " : " + str(exc),
            errorCode=ERROR_CODE.INTERNAL_ERROR,
            meta={"path": str(request.url)}
        ).model_dump()
    )
