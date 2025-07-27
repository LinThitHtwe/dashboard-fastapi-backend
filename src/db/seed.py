import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.database import engine, SessionLocal, Base
from models.product_model import Product
from faker import Faker
import asyncio
import random

fake = Faker()

def generate_product_name():
    adjective = fake.word(ext_word_list=[
        "Durable", "Portable", "Smart", "Wireless", "Compact",
        "Eco", "Ergonomic", "Elegant", "High-Speed", "Lightweight"
    ])
    material = fake.word(ext_word_list=[
        "Steel", "Wood", "Plastic", "Silicone", "Glass",
        "Cotton", "Leather", "Metal", "Rubber", "Carbon"
    ])
    product_type = fake.word(ext_word_list=[
        "Headphones", "Backpack", "Chair", "Notebook", "Shoes",
        "Watch", "Bottle", "T-shirt", "Phone", "Lamp"
    ])
    return f"{adjective} {material} {product_type}"

async def seed():
    async with SessionLocal() as session:
        BATCH_SIZE = 100  
        TOTAL_BATCHES = 1000  # 100 * 1000 = 100,000 products

        for _ in range(TOTAL_BATCHES):
            products = [
                Product(
                    name=generate_product_name(),
                    category=fake.random_element(elements=("Tech", "Books", "Clothes", "Home", "Toys")),
                    description=fake.sentence(nb_words=12),
                    price=round(random.uniform(1.0, 1000.0), 2),
                    stock=random.randint(0, 200),
                    rating=round(random.uniform(0.0, 5.0), 1),
                )
                for _ in range(BATCH_SIZE)
            ]
            session.add_all(products)
            await session.flush() 
        await session.commit()

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed()

if __name__ == "__main__":
    asyncio.run(main())
