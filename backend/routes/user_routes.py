from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from ..db import get_db
from ..routes.auth_routes import get_current_user, get_password_hash

router = APIRouter()

class User(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


@router.get("/users")
def get_users(current_user=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, name, email FROM mock_data")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@router.post("/users", status_code=201)
def create_user(user: User, current_user=Depends(get_current_user)):
    hashed_password = get_password_hash(user.password)

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO mock_data (name, email, password) VALUES (%s, %s, %s)",
        (user.name, user.email, hashed_password)
    )
    conn.commit()
    cur.close()
    conn.close()

    return {"message": "User created"}


@router.put("/users/{id}")
def update_user(id: int, user: User, current_user=Depends(get_current_user)):
    hashed_password = get_password_hash(user.password)

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE mock_data SET name=%s, email=%s, password=%s WHERE id=%s",
        (user.name, user.email, hashed_password, id)
    )
    conn.commit()

    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")

    cur.close()
    conn.close()
    return {"message": "User updated"}


@router.patch("/users/{id}")
def patch_user(id: int, user: UserUpdate, current_user=Depends(get_current_user)):
    parts = []
    values = []

    if user.name:
        parts.append("name=%s")
        values.append(user.name)
    if user.email:
        parts.append("email=%s")
        values.append(user.email)

    if not parts:
        raise HTTPException(status_code=400, detail="No fields to update")

    values.append(id)

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        f"UPDATE mock_data SET {', '.join(parts)} WHERE id=%s",
        tuple(values)
    )
    conn.commit()

    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")

    cur.close()
    conn.close()
    return {"message": "User patched"}


@router.delete("/users/{id}")
def delete_user(id: int, current_user=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM mock_data WHERE id=%s", (id,))
    conn.commit()

    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")

    cur.close()
    conn.close()
    return {"message": "User deleted"}
