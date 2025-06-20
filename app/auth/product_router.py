from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_db
from app.models.user import Product
from app.auth.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.auth.utils import admin_required

router = APIRouter(prefix="/products", tags=["Products"])

# Create a new product (Admin only)
@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):
    """
    Create a new product. (Admin only)
    """
    try:
        new_product = Product(**product.dict())
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all products
@router.get("/", response_model=List[ProductResponse])
async def get_products(db: Session = Depends(get_db)):
    """
    Get all products.
    """
    try:
        return db.query(Product).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get a specific product by ID
@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get a product by ID.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Update a product (Admin only)
@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):
    """
    Update a product by ID. (Admin only)
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in update.dict(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

# Delete a product (Admin only)
@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):
    """
    Delete a product by ID. (Admin only)
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}
