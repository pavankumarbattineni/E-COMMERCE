from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.session import Base
from sqlalchemy import DateTime, func
from sqlalchemy.orm import relationship

# user model definition

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String, index=True, comment="Full name of the user")  
    email = Column(String, unique=True, index=True,comment="Email address of the user")
    hashed_password = Column(String, comment="Hashed password of the user")
    is_admin = Column(Integer, default=0, nullable=False, comment="Flag to indicate if the user is an admin")

    orders = relationship("Order", back_populates="user")

    
# category model definition

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False, comment="Name of the category")
    description = Column(String, nullable=True, comment="Description of the category")
    image_url = Column(String, nullable=True, comment="URL of the category image")


# product model definition

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, comment="Name of the product")
    description = Column(String, nullable=True, comment="Description of the product"    )
    price = Column(Integer, nullable=False, comment="Price of the product")
    stock = Column(Integer, default=0, nullable=False, comment="Stock quantity of the product")
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=False, comment="Foreign key to the categories table")
    image_url = Column(String, nullable=True, comment="URL of the product image")


# order model definition


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total_amount = Column(Integer, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"))
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
