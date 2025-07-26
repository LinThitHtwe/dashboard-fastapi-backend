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

app = FastAPI(title = "Product API")

@app.on_event("startup")
async def startup():
    redis_backend = RedisBackend(redis.from_url("redis://localhost"))
    FastAPICache.init(redis_backend, prefix="fastapi-cache")

# Global exception handlers
app.add_exception_handler(SQLAlchemyError, db_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

origins = [
    "http://localhost:3000",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.get("/")
# def root():
#     return {"Message": "Hellloooo"}

app.include_router(product.router)