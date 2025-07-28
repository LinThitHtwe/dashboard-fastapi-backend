from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, desc
from typing import Optional
from src.models.product_model import Product
from src.schemas.product_schema import ProductCreate, ProductOut
from sqlalchemy.exc import SQLAlchemyError
from src.common.logger import logger  

async def get_products_list_service(
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

    logger.debug("Fetching product list with filters: "
                    f"category={category}, min_price={min_price}, max_price={max_price}, "
                    f"name={name}, sort_by={sort_by}, sort_dir={sort_dir}, skip={skip}, limit={limit}")
    
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

    logger.info(f"Fetched {len(products)} products from the database")
    
    return [ProductOut.model_validate(p) for p in products]

async def get_product_by_id_service(product_id: int, db: AsyncSession) -> ProductOut:
    try:
        logger.debug(f"Fetching product by ID: {product_id}")
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalars().first()

        if not product:
            logger.warning(f"Product not found: {product_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        logger.info(f"Product found: {product_id}")

        return ProductOut.model_validate(product)

    except SQLAlchemyError as e:
        logger.error(f"Database error while getting product {product_id}: {e}")
        raise

async def create_product_service(product: ProductCreate, db: AsyncSession) -> ProductOut:
    try:
        logger.debug(f"Creating product: {product.name}")
        db_product = Product(**product.model_dump())
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)

        logger.info(f"Product created successfully: {db_product.id}")

        return ProductOut.model_validate(db_product)

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while creating product: {e}")
        raise

async def update_product_service(product_id: int, updated: ProductCreate, db: AsyncSession) -> ProductOut:
    try:
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalars().first()

        if not product:
            logger.warning(f"Product not found for update: {product_id}")
            raise HTTPException(status_code=404, detail="Product not found")

        for field, value in updated.model_dump().items():
            setattr(product, field, value)

        await db.commit()
        await db.refresh(product)

        logger.info(f"Product updated successfully: {product_id}")

        return ProductOut.model_validate(product)

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while updating product {product_id}: {e}")
        raise
