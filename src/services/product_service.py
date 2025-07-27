import time
from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, desc
from typing import Optional
from src.models.product_model import Product
from src.schemas.product_schema import ProductOut
from src.common.response_base_model import Result
from sqlalchemy.exc import SQLAlchemyError

async def get_products_list(
    db: AsyncSession,
    skip: int,
    limit: int,
    sort_by: str,
    sort_dir: str,
    category: Optional[str],
    min_price: Optional[float],
    max_price: Optional[float],
    name: Optional[str]
):

    query = select(Product)

    if category:
        query = query.where(Product.category.ilike(f"%{category}%"))
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    if name:
        query = query.where(Product.name.ilike(f"%{name}%"))

    sort_column = getattr(Product, sort_by)
    query = query.order_by(desc(sort_column) if sort_dir == "desc" else asc(sort_column))
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    products = result.scalars().all()

    
    return [ProductOut.model_validate(p) for p in products]

async def get_product_by_id(product_id: int, db: AsyncSession) -> ProductOut:
    start_time = time.time()

    try:
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalars().first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        elapsed_time = (time.time() - start_time) * 1000  
        if elapsed_time > 100:
            print(f"get_product_by_id({product_id}) took {elapsed_time:.2f}ms")

        return ProductOut.model_validate(product)

    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise
