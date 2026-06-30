// equivalents of node and python 
Node.js	             Python/FastAPI
bcrypt	             passlib[bcrypt]
jsonwebtoken	     python-jose
bcrypt.hash()	     pwd_context.hash()
bcrypt.compare()	 pwd_context.verify()
 
<!-- JWT -->

CryptContext → sets up bcrypt as the hashing algorithm
hash_password() → converts plain text to hash
verify_password() → compares plain text against stored hash

<!-- how everything is connected -->
models.py imports Base from database.py
    ↓
User class inherits Base
    ↓
SQLAlchemy registers User against Base's metadata
    ↓
Base.metadata now knows about the users table and its columns
    ↓
create_all(bind=engine) looks at all registered tables
    ↓
generates and runs this SQL:
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name VARCHAR,
    email VARCHAR UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    password VARCHAR
)
    ↓
app.db gets the table with all columns


<!-- Deployment -->

Step 1: requirements.txt
First, update your requirements.txt — this is what the server uses to install dependencies:
pip freeze > requirements.txt

Step 2: Production Server
In development you used --reload flag. In production never use --reload — it's slow and insecure.
Production command:
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

--host 0.0.0.0 → accept connections from anywhere
--workers 4 → run 4 parallel processes (handle more requests)
No --reload → faster and safer


Step 3: Environment Variables in Production
Never copy your .env file to the server. Instead set environment variables directly on the server:
export SECRET_KEY="your-production-secret-key"
export ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES=30
Or use the platform's built-in environment variable manager (Railway, Render, AWS all have this).

Step 4: Deployment Platforms
For a FastAPI app, the easiest platforms to deploy on:
PlatformFree TierDifficultyRailway✅⭐ EasiestRender✅⭐ EasyFly.io✅⭐⭐ MediumAWS/GCP❌⭐⭐⭐ Complex
For your first deployment → Railway or Render are the best choices.

Step 5: Procfile
Some platforms need a Procfile to know how to start your app:
web: uvicorn main:app --host 0.0.0.0 --port $PORT
Create it:
touch Procfile
Add that line inside it.

Step 6: Switch to PostgreSQL for Production
SQLite is fine for development but not for production — it's a file-based DB that doesn't handle multiple workers well.
In production use PostgreSQL. The only change needed is in database.py:
python# development
DATABASE_URL = "sqlite:///./app.db"

# production
DATABASE_URL = "postgresql://user:password@host/dbname"
Store DATABASE_URL in your .env file:
pythonfrom dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

That's the deployment overview! You don't need to deploy right now — but you know exactly what's needed when you're ready.