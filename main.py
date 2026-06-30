# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import Optional

# app = FastAPI()

# @app.get('/')
# async def read_root():
#     return {"message" : "Heyyy!!!!"}

# # @app.get('/greet/{name}')
# # async def greet_user(name:str):
# #     return {'message': f"Hello, {name}!!"}

# @app.get('/city/{city_name}')
# async def city_details(city_name: str):
#     return {'city': f"{city_name}", 'country': 'India'}

# @app.get('/products')
# async def product_details(category: str, in_stock: bool):
#     return {'message': f'Product category {category} is {in_stock}'}

# @app.get('/user/{user_id}', status_code=200)
# async def get_user(user_id: int):
#     if user_id == 1:
#         return {'id': 1, 'name': 'john'}
#     raise HTTPException(status_code=404, detail="item not found")

# @app.get('/greet/{name}', status_code=200)
# async def greet(name:str, lang: str = 'en'):
#     greetings = {
#         "en" : 'Hello',
#         "es" : 'Hola',
#         "fr" : 'Bonjour'
#     }
    
#     if lang not in greetings:
#         raise HTTPException(status_code=400, detail="Unsupportedddd language")
#     return {'message': f"{greetings[lang]}, {name}"}

# class User(BaseModel):
#     name: str
#     age: int
#     email: str
    
# @app.post('/users', status_code=200)
# async def create_user(user: User):
#     return {'message': f"User {user.name} created!!", 'data': user}


# class Product(BaseModel):
#     name: str
#     price: float
#     in_stock: bool = True
#     description: Optional[str] = None
#     discount: Optional[float] = 0.0
    
# @app.post('/products', status_code=201)
# async def create_product(product: Product):
#     return {'message': f'{product.name} created!!', 'data': product}


# class Address(BaseModel):
#     street: str
#     city: str
#     pincode: str
    
# class Order(BaseModel):
#     order_id: int
#     customer_name: str
#     address: Address
    
# @app.post('/orders', status_code=201)
# async def create_order(order: Order):
#     return {'message': "Order Placed", "data": order}

# class ProductIn(BaseModel):
#     name: str
#     price: float
#     cost_price: float

# class ProductOut(BaseModel):
#     name: str
#     price: float
#     cost: Optional[float] = None
#     desc: Optional[str] = None

# @app.post('/secure-products', response_model=ProductOut, status_code=201)
# async def products(product: ProductIn):
#     return product
    
from fastapi import FastAPI, Depends, HTTPException
from database import engine, Base, get_db
from models import User
from schemas import UserCreate, UserOut, UserLogin, UserToken
from sqlalchemy.orm import Session
from auth import hash_password, verify_password, create_access_token
from oauth2 import get_current_user
import time
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
Base.metadata.create_all(bind=engine)

# 1: UserCreate here is from model -> server to database
# 2: UserOut needs to be same in name as the User model
# 3: if not the return new_user has to be implicitly returned with the 
#   field values.
#   return {
#     "id": new_user.id,
#     "name": new_user.name,
#     "email": new_user.email,
#     "is_active": new_user.is_active
#   }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # code here runs BEFORE the route
    response = await call_next(request)  # runs the actual route
    
    # code here runs AFTER the route
    process_time = time.time() - start_time
    print(f"{request.method} {request.url} - {process_time:.4f}s")
    
    return response


@app.post('/users', response_model=UserOut, status_code=201)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# get all users
@app.get('/users', response_model=list[UserOut], status_code=200)
async def get_users(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    query=db.query(User).all()
    return query if len(query) > 0 else {'message': 'There are no users to display'}

# get user by id
@app.get('/users/{user_id}', response_model=UserOut, status_code=200)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    query=db.query(User).filter(User.id == user_id).first()
    if not query:
        raise HTTPException(status_code=404, detail='User not found')
    return query


# update user details using put
@app.put('/users/{user_id}', response_model=UserOut, status_code=200)
async def update_user_details(user_id: int, new_data: UserCreate, db:Session = Depends(get_db)):
    query = query=db.query(User).filter(User.id == user_id).first()
    if not query:
        raise HTTPException(status_code=404, detail='user not found for this id')
    else:
        query.name = new_data.name
        query.email = new_data.email
        db.commit()
        db.refresh(query)
        return query
    
@app.delete('/users/{user_id}',status_code=200)
async def delete_user_by_id(user_id: int, db:Session = Depends(get_db)):
    query=db.query(User).filter(User.id == user_id).first()
    if not query:
        raise HTTPException(status_code=404, detail='user not found for this id')
    else:
       db.delete(query)
       db.commit()
       return {'message': 'User deleted Successfully!!'}
    
 
@app.post('/register',response_model=UserOut, status_code=201)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(user.password)
    new_user = User(name=user.name, email=user.email, password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user 

@app.post('/login', response_model=UserToken, status_code=200)
def user_login(user: UserLogin, db:Session = Depends(get_db)):
    is_user = db.query(User).filter(User.email == user.email).first()
    if not is_user:
        raise HTTPException(status_code=400, detail='User doesnot exist!!')
    else:
        hashed = hash_password(user.password)
        password_valid = verify_password(user.password, is_user.password)
        if not password_valid:
            raise HTTPException(status_code=401, detail='Incorrect Password!!')
        return {'access_token': create_access_token(dict(user))}

    