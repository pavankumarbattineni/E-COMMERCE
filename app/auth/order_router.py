from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload  # ✅ added joinedload
from typing import List
from app.database.db import get_db
from app.auth.schemas import OrderCreate, OrderResponse
from app.models.user import Order, OrderItem, Product
from app.auth.utils import get_current_user
from app.models.user import User
from app.auth.utils import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new order for the current user.
    Validates product stock and calculates total amount.
    If any product is out of stock, raises an HTTPException.
    """
    try:
        total_amount = 0
        order_items = []

        for item in order_data.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product ID {item.product_id} not found")
            if product.stock < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
            
            product.stock -= item.quantity
            total_amount += product.price * item.quantity
            order_items.append({"product_id": product.id, "quantity": item.quantity, "price": product.price})

        new_order = Order(user_id=current_user.id, total_amount=total_amount)
        db.add(new_order)
        db.flush()

        for item in order_items:
            db.add(OrderItem(order_id=new_order.id, **item))

        db.commit()
        db.refresh(new_order)

        # ✅ Add product_name dynamically for each item
        for item in new_order.items:
            item.product_name = item.product.name if item.product else "Unknown Product"

        return new_order

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Order creation failed: {str(e)}")


@router.get("/", response_model=List[OrderResponse])
async def get_user_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch all orders for the current user.
        Returns a list of orders associated with the user."""
    try:
        orders = (
            db.query(Order)
            .filter(Order.user_id == current_user.id)
            .options(joinedload(Order.items).joinedload(OrderItem.product))  # ✅ Eager-load related products
            .all()
        )

        # Add product_name to each item
        for order in orders:
            for item in order.items:
                item.product_name = item.product.name if item.product else "Unknown Product"

        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch orders: {str(e)}")


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_by_id(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch a specific order by ID for the current user.
        Returns the order details if found, otherwise raises a 404 error."""
    try:
        order = (
            db.query(Order)
            .filter(Order.id == order_id, Order.user_id == current_user.id)
            .options(joinedload(Order.items).joinedload(OrderItem.product))  # ✅ Eager-load products
            .first()
        )
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        #  Add product_name to each item
        for item in order.items:
            item.product_name = item.product.name if item.product else "Unknown Product"

        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch order: {str(e)}")


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing order for the current user.
        Validates product stock and updates the order items.
        If any product is out of stock, raises an HTTPException."""
    try:
        order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Clear existing items and refund stock
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock += item.quantity
            db.delete(item)

        total_amount = 0
        new_items = []

        for item in order_data.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product ID {item.product_id} not found")
            if product.stock < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
            
            product.stock -= item.quantity
            total_amount += product.price * item.quantity
            new_items.append(OrderItem(order_id=order.id, product_id=product.id, quantity=item.quantity, price=product.price))

        for item in new_items:
            db.add(item)

        order.total_amount = total_amount
        db.commit()
        db.refresh(order)

        #  Add product_name dynamically
        for item in order.items:
            item.product_name = item.product.name if item.product else "Unknown Product"

        return order

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update order: {str(e)}")


@router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an order by ID for the current user.
        Restores stock for the products in the order and removes the order from the database."""
    try:
        order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Restore stock
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock += item.quantity
            db.delete(item)

        db.delete(order)
        db.commit()
        return {"message": "Order deleted successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete order: {str(e)}")
