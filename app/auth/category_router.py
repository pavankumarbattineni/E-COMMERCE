from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_db
from app.models.user import Category
from app.auth.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from app.auth.utils import admin_required

router = APIRouter(prefix="/categories", tags=["Categories"])

# Create a new category (Admin only)
@router.post("/", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):
    """
    Create a new category. (Admin only)
    """
    try:
        existing = db.query(Category).filter(Category.name == category.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category already exists")
        new_category = Category(**category.dict())
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create category: {str(e)}")

# Get all categories
@router.get("/", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """
    Get all categories.
    """
    try:
        return db.query(Category).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch categories: {str(e)}")

# Get a specific category by ID
@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    Get a category by ID.
    """
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch category: {str(e)}")

# Update a category (Admin only)
@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):
    """
    Update a category by ID. (Admin only)
    """
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        for key, value in update.dict(exclude_unset=True).items():
            setattr(category, key, value)
        db.commit()
        db.refresh(category)
        return category
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update category: {str(e)}")

# Delete a category (Admin only)
@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required)
):
    """
    Delete a category by ID. (Admin only)
    """
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        db.delete(category)
        db.commit()
        return {"message": "Category deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete category: {str(e)}")
