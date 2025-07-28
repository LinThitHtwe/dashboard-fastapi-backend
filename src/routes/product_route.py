from fastapi import APIRouter,Query, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.cache_utils import get_or_set_cache
from src.services.product_service import create_product_service, get_product_by_id_service, get_products_list_service, update_product_service
from src.schemas.product_schema import ProductCreate, ProductOut
from src.db.database import get_db

from typing import Optional
from src.common.response_base_model import Result
from src.common.logger import logger  


router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/{product_id}", response_model=Result[ProductOut])
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"GET /products/{product_id} - Fetching product")

    cache_key = f"product:{product_id}"

    async def fetch_product_by_id():
        product = await get_product_by_id_service(
            db=db,
            product_id=product_id
        )
        return product.model_dump()

    cached_data = await get_or_set_cache(
        key=cache_key,
        expire=60,
        fetch_func=fetch_product_by_id
    )

    if not cached_data:
        raise HTTPException(status_code=404, detail="Product not found")

    return Result.ok(data=cached_data, message="Product fetched successfully")

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
    logger.info("GET /products - Listing products")

    cache_key = f"products:list:{skip}:{limit}:{sort_by}:{sort_dir}:{category}:{min_price}:{max_price}:{name}"

    async def fetch_products():
        return [
            product.model_dump()
            for product in await get_products_list_service(
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


    return Result.ok(
        data=[ProductOut(**p) for p in cached_data],
        message="Products retrieved (cache/db)",
        meta={
            "count": len(cached_data),
            "skip": skip,
            "limit": limit,
            "sort_by": sort_by,
            "sort_dir": sort_dir,
        }
    )

@router.get("/test-error")
async def test_generic_error():
    raise Exception("This is a test for generic error")

@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"POST /products - Creating product: {product.name}")
    return await create_product_service(product, db)

@router.put("/{product_id}", response_model=ProductOut)
async def update_product(product_id: int, updated: ProductCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"PUT /products/{product_id} - Updating product")
    return await update_product_service(product_id=product_id, updated=updated, db=db)

