from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

# bcrypt is the hashing algorithm - same as bcrypt in Node.js
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# SECRET_KEY - used to sign the token, never commit this to git
# In production, store this in environment variables
SECRET_KEY = "your-secret-key"

# HS256 - standard JWT signing algorithm
ALGORITHM = "HS256"

# token expires after 30 minutes - after this, user must login again
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # compares plain text against stored hash - never compare plain text directly
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()  # copy so we don't mutate the original dict
    
    # datetime.now(timezone.utc) is the modern way - utcnow() is deprecated in Python 3.12+
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # "exp" is a standard JWT claim - python-jose automatically rejects expired tokens
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        # algorithms expects a list - you could support multiple algorithms
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        # catches both invalid tokens and expired tokens
        return None