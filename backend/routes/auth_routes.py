from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from ..db import get_db
from fastapi.security import OAuth2PasswordBearer
from fastapi import Security
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# in a real app load from env
SECRET_KEY = "CHANGE_THIS_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class RegisterModel(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginModel(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_user_by_id(user_id: int):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, name, email FROM mock_data WHERE id=%s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def get_current_user(token: str = Security(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/register", status_code=201)
def register(user: RegisterModel):
    conn = get_db()
    cur = conn.cursor()
    # check existing
    cur.execute("SELECT id FROM users WHERE email=%s", (user.email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = get_password_hash(user.password)
    cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (user.name, user.email, hashed))
    conn.commit()
    user_id = cur.lastrowid
    cur.close()
    conn.close()
    return {"message": "User registered", "id": user_id}


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    # OAuth2 uses "username", we treat it as email
    cur.execute("SELECT * FROM mock_data WHERE email=%s", (form_data.username,))
    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row or not verify_password(form_data.password, row["password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(row["id"])},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}
