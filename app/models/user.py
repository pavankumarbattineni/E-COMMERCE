from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database.session import Base


# user model definition

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String, index=True, comment="Full name of the user")  
    email = Column(String, unique=True, index=True,comment="Email address of the user")
    hashed_password = Column(String, comment="Hashed password of the user")
    is_admin = Column(Integer, default=0, nullable=False, comment="Flag to indicate if the user is an admin")
    
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
