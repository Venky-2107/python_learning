from fastapi import APIRouter, HTTPException
from schemas import UserCreate, UserOut, UserToken, UserLogin
from fastapi import Depends, HTTPException
from database import get_db
from models import User
from sqlalchemy.orm import Session
from auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post('/register',response_model=UserOut, status_code=201)
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

@router.post('/login', response_model=UserToken, status_code=200)
def user_login(user: UserLogin, db:Session = Depends(get_db)):
    is_user = db.query(User).filter(User.email == user.email).first()
    if not is_user:
        raise HTTPException(status_code=400, detail='User doesnot exist!!')
    else:
        password_valid = verify_password(user.password, is_user.password)
        if not password_valid:
            raise HTTPException(status_code=401, detail='Incorrect Password!!')
        return {'access_token': create_access_token(dict(user))}


