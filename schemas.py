from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    
class UserLogin(BaseModel):
    email: str
    password: str
    
class UserOut(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    
    class Config:
        from_attributes = True

class UserToken(BaseModel):
    access_token: str
    token_type: str = 'Bearer'
    
    
# When you return new_user (a SQLAlchemy object), Pydantic does this:
# new_user.id        → UserOut.id
# new_user.name      → UserOut.name
# new_user.email     → UserOut.email
# new_user.is_active → UserOut.is_active
# It maps by field name — Pydantic looks at each field in UserOut and finds 
# the matching attribute on the returned object
# But wait — new_user is a SQLAlchemy object, not a dict. How does Pydantic read it?
# That's because of a Pydantic setting called from_attributes (previously 
# called orm_mode in older versions). It tells Pydantic:

# "Don't just look for dict keys — also look for object attributes".
