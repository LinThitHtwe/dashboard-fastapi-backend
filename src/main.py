from fastapi import FastAPI
from src.routes import product_route as product
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as redis
from src.common.exception_handler import (
    db_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    global_exception_handler
)
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from contextlib import asynccontextmanager

#app = FastAPI(title = "Product API")

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_backend = RedisBackend(redis.from_url(settings.REDIS_URL))
    FastAPICache.init(redis_backend, prefix="fastapi-cache")
    print("Redis cache initialized")
    print(settings.REDIS_URL)

    yield

    print(" App is shutting down... (if needed)")

app = FastAPI(lifespan=lifespan,title = "Product API", description="API for managing products", version="1.0.0")

# Global exception handlers
app.add_exception_handler(SQLAlchemyError, db_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.get("/")
# def root():
#     return {"Message": "Hellloooo"}

app.include_router(product.router)