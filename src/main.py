from fastapi import FastAPI
from src.routes import product as product

app = FastAPI(title = "FastAPI Rest API")

@app.get("/")
def root():
    return {"Message": "Hellloooo"}

app.include_router(product.router)