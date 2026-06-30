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