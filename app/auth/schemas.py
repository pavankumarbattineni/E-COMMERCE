from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# schema for user creation

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=8)
    is_admin: int = Field(default=0, ge=0, le=1)  # Assuming is_admin is a binary flag (0 or 1)

# schema for user login

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

# schema for token response

class Token(BaseModel):
    access_token: str
    token_type: str

# schema for token data for decoding

class TokenData(BaseModel):
    email: str | None = None

#schema for returning user data

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_admin: int

    model_config = {
        "from_attributes": True
    }




# schema for category creation

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int

    model_config = {
        "from_attributes": True
    }

    

# schema for product creation


# schema for product creation and response

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    stock: int
    category_id: int
    image_url: Optional[str] = None

# schema for product creation
class ProductCreate(ProductBase):
    pass

# schema for product update

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None

# schema for product response

class ProductResponse(ProductBase):
    id: int

    model_config = {
        "from_attributes": True
    }
