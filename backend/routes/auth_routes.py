from fastapi import APIRouter, HTTPException, Depends, Security
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from ..db import get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter()

# ✅ FIXED bcrypt configuration (stable)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# 🔐 JWT Config
SECRET_KEY = "CHANGE_THIS_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ---------- MODELS ----------

class RegisterModel(BaseModel):
    name: str
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- PASSWORD UTILS ----------

def get_password_hash(password: str) -> str:
    # bcrypt max safe limit handled internally
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ---------- JWT UTILS ----------

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# ---------- USER HELPERS ----------

def get_user_by_id(user_id: int):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "SELECT id, name, email FROM mock_data WHERE id=%s",
        (user_id,)
    )

    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


def get_current_user(token: str = Security(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = get_user_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# ---------- ROUTES ----------

@router.post("/register", status_code=201)
def register(user: RegisterModel):
    conn = get_db()
    cur = conn.cursor()

    # Check existing email
    cur.execute(
        "SELECT id FROM mock_data WHERE email=%s",
        (user.email,)
    )
    if cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_password = get_password_hash(user.password)

    # Insert user
    cur.execute(
        "INSERT INTO mock_data (name, email, password) VALUES (%s, %s, %s)",
        (user.name, user.email, hashed_password)
    )

    conn.commit()
    user_id = cur.lastrowid

    cur.close()
    conn.close()

    return {
        "message": "User registered successfully",
        "id": user_id
    }


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "SELECT * FROM mock_data WHERE email=%s",
        (form_data.username,)
    )
    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(
        data={"sub": str(user["id"])},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
