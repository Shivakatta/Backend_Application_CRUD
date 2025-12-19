from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from ..db import get_db
from ..routes.auth_routes import get_current_user, get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


# -------------------------------
# MODELS
# -------------------------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


# -------------------------------
# ROUTES
# -------------------------------

# 🔐 GET ALL USERS
@router.get("")
def get_users(current_user=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT id, name, email FROM mock_data")
    users = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "count": len(users),
        "data": users
    }


# 🔐 CREATE USER
@router.post("", status_code=201)
def create_user(user: UserCreate, current_user=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    # check duplicate email
    cur.execute(
        "SELECT id FROM mock_data WHERE email=%s",
        (user.email,)
    )
    if cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_password = get_password_hash(user.password)

    cur.execute(
        "INSERT INTO mock_data (name, email, password) VALUES (%s, %s, %s)",
        (user.name, user.email, hashed_password)
    )

    conn.commit()
    user_id = cur.lastrowid

    cur.close()
    conn.close()

    return {
        "message": "User created successfully",
        "id": user_id
    }


# 🔐 FULL UPDATE (PUT)
@router.put("/{id}")
def update_user(id: int, user: UserCreate, current_user=Depends(get_current_user)):
    hashed_password = get_password_hash(user.password)

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE mock_data
        SET name=%s, email=%s, password=%s
        WHERE id=%s
        """,
        (user.name, user.email, hashed_password, id)
    )

    conn.commit()

    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    cur.close()
    conn.close()

    return {"message": "User updated successfully"}


# 🔐 PARTIAL UPDATE (PATCH)
@router.patch("/{id}")
def patch_user(id: int, user: UserUpdate, current_user=Depends(get_current_user)):
    fields = []
    values = []

    if user.name is not None:
        fields.append("name=%s")
        values.append(user.name)

    if user.email is not None:
        fields.append("email=%s")
        values.append(user.email)

    if user.password is not None:
        fields.append("password=%s")
        values.append(get_password_hash(user.password))

    if not fields:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    values.append(id)

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        f"UPDATE mock_data SET {', '.join(fields)} WHERE id=%s",
        tuple(values)
    )

    conn.commit()

    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    cur.close()
    conn.close()

    return {"message": "User updated successfully"}


# 🔐 DELETE USER
@router.delete("/{id}")
def delete_user(id: int, current_user=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM mock_data WHERE id=%s", (id,))
    conn.commit()

    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    cur.close()
    conn.close()

    return {"message": "User deleted successfully"}
