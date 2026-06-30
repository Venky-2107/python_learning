from fastapi import APIRouter
from fastapi import Depends, HTTPException
from database import get_db
from models import User
from schemas import UserCreate, UserOut
from sqlalchemy.orm import Session
from oauth2 import get_current_user

router = APIRouter()

@router.post('/users', response_model=UserOut, status_code=201)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# get all users
@router.get('/users', response_model=list[UserOut], status_code=200)
async def get_users(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    query=db.query(User).all()
    return query

# get user by id
@router.get('/users/{user_id}', response_model=UserOut, status_code=200)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    query=db.query(User).filter(User.id == user_id).first()
    if not query:
        raise HTTPException(status_code=404, detail='User not found')
    return query


# update user details using put
@router.put('/users/{user_id}', response_model=UserOut, status_code=200)
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
    
@router.delete('/users/{user_id}',status_code=200)
async def delete_user_by_id(user_id: int, db:Session = Depends(get_db)):
    query=db.query(User).filter(User.id == user_id).first()
    if not query:
        raise HTTPException(status_code=404, detail='user not found for this id')
    else:
       db.delete(query)
       db.commit()
       return {'message': 'User deleted Successfully!!'}