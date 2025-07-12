from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal, create_tables
from schemas import ProductCreate, ProductUpdate, ProductResponse
from crud import create_product, get_product, get_product_by_id, update_product, delete_product
from auth import get_current_user
from jose import jwt
from fastapi.security import OAuth2PasswordRequestForm
from models import User
from datetime import timedelta, datetime
from auth import verify_password


app = FastAPI()
create_tables()


SECRET_KEY = "secret123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# List all products


@app.get("/products", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return get_product(db)

# Get product by ID


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

# Create Product


@app.post("/products", response_model=ProductResponse)
def create(product: ProductCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return create_product(db, product)

# Update product


@app.put("/products/{product_id}", response_model=ProductResponse)
def update(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    updated = update_product(db, product_id, data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return updated

# Delete product


@app.delete("/products/{product_id}", response_model=ProductResponse)
def delete(product_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    deleted = delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return deleted


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    to_encode = {"sub": user.username,
                 "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}
