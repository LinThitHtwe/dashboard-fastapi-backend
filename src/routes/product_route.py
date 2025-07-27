from fastapi import APIRouter,Query, Depends, HTTPException, status
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.common.cache_utils import get_or_set_cache
from src.services.product_service import get_product_by_id, get_products_list
from src.models.product_model import Product
from src.schemas.product_schema import ProductCreate, ProductOut
from src.db.database import get_db
import time
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from sqlalchemy import select, asc, desc
from typing import Optional
from src.common.response_base_model import Result
from fastapi_cache.decorator import cache
from src.core.config import settings
from src.core.redis_client import redis_client
import json


router = APIRouter(prefix="/products", tags=["Products"])

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

@router.get("/ping")
async def ping():
    cache_key = "ping-response"

    cached = await r.get(cache_key)
    print(f"Cache hit: {cached }")
    if cached:
        return {"message": "pong (from cache)", "cached": cached}

    result = "pong"
    await r.set(cache_key, result, ex=30)  # expire in 30 seconds

    return {"message": "pong (fresh)", "cached": result}

@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    start_time = time.time()  

    try:
        db_product = Product(**product.model_dump())
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)

        elapsed_time = (time.time() - start_time) * 1000  
        #if elapsed_time > 100:
        print(f"⚠️ Create Product API took {elapsed_time:.2f}ms")

        return db_product

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product due to a server error."
        )
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product data."
        )

@router.get("/{product_id}", response_model=Result[ProductOut])
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    start_time = time.time()

    cache_key = f"product:{product_id}"

    async def fetch_product_by_id():
        product = await get_product_by_id(
            db=db,
            product_id=product_id
        )
        return product.model_dump()

    cached_data = await get_or_set_cache(
        key=cache_key,
        expire=60,
        fetch_func=fetch_product_by_id
    )

    elapsed = round((time.time() - start_time) * 1000, 2)
    if not cached_data:
        raise HTTPException(status_code=404, detail="Product not found")

    return Result.ok(data=cached_data, message="Product fetched successfully", meta={
        "elapsed_ms": elapsed
    })

@router.get("/", response_model=Result[list[ProductOut]])
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("id", pattern="^(id|price|stock|rating|created_at)$"),
    sort_dir: str = Query("asc", pattern="^(asc|desc)$"),
    category: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    name: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    start_time = time.time()

    cache_key = f"products:list:{skip}:{limit}:{sort_by}:{sort_dir}:{category}:{min_price}:{max_price}:{name}"

    async def fetch_products():
        return [
            product.model_dump()
            for product in await get_products_list(
                db=db,
                skip=skip,
                limit=limit,
                sort_by=sort_by,
                sort_dir=sort_dir,
                category=category,
                min_price=min_price,
                max_price=max_price,
                name=name
            )
        ]

    cached_data = await get_or_set_cache(
        key=cache_key,
        expire=60,
        fetch_func=fetch_products
    )

    elapsed = round((time.time() - start_time) * 1000, 2)

    return Result.ok(
        data=[ProductOut(**p) for p in cached_data],
        message="Products retrieved (cache/db)",
        meta={
            "count": len(cached_data),
            "skip": skip,
            "limit": limit,
            "sort_by": sort_by,
            "sort_dir": sort_dir,
            "elapsed_ms": elapsed
        }
    )


@router.get("/test-error")
async def test_generic_error():
    raise Exception("This is a test for generic error")

@router.put("/{product_id}", response_model=ProductOut)
async def update_product(product_id: int, updated: ProductCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in updated.dict().items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)
    return product

# @router.delete("/{product_id}")
# async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Product).where(Product.id == product_id))
#     product = result.scalars().first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")

#     await db.delete(product)
#     await db.commit()
#     return {"detail": "Product deleted successfully"}
