from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

def get_current_user(token:str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(status_code=401, detail='user not authenticated')    
    
    return payload

        