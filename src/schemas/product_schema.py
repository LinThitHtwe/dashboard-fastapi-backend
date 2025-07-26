from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    stock: int = Field(ge=0, default=0)
    rating: Optional[float] = Field(default=0.0, ge=0.0, le=5.0)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)

class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
