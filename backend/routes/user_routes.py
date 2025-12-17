from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from ..db import get_db

router = APIRouter()


class UserCreate(BaseModel):
    name: str
    email: EmailStr


class User(BaseModel):
    name: str
    email: EmailStr


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


@router.get("/users")
def get_users():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM mock_data")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@router.post("/users", status_code=201)
def create_user(user: User):
    if not user.name or not user.email:
        raise HTTPException(status_code=400, detail="Name and email required")

    conn = None
    cur = None
    try:
        conn = get_db()
        cur = conn.cursor()
        sql = "INSERT INTO mock_data (name, email) VALUES (%s, %s)"
        cur.execute(sql, (user.name, user.email))
        conn.commit()
        user_id = cur.lastrowid
    except Exception as e:
        if conn is not None:
            try:
                conn.rollback()
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cur is not None:
            try:
                cur.close()
            except Exception:
                pass
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass

    return {"message": "User added successfully", "id": user_id}


@router.put("/users/{id}")
def update_user(id: int, user: UserCreate):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE mock_data SET name=%s, email=%s WHERE id=%s",
        (user.name, user.email, id),
    )
    conn.commit()
    affected = cur.rowcount
    cur.close()
    conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated"}


@router.patch("/users/{id}")
def patch_user(id: int, user: UserUpdate):
    if user.name is None and user.email is None:
        raise HTTPException(status_code=400, detail="No fields to update")

    parts = []
    params = []
    if user.name is not None:
        parts.append("name=%s")
        params.append(user.name)
    if user.email is not None:
        parts.append("email=%s")
        params.append(user.email)
    params.append(id)
    sql = f"UPDATE mock_data SET {', '.join(parts)} WHERE id=%s"

    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql, tuple(params))
    conn.commit()
    affected = cur.rowcount
    cur.close()
    conn.close()

    if affected == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User patched"}


@router.delete("/users/{id}")
def delete_user(id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM mock_data WHERE id=%s", (id,))
    conn.commit()
    affected = cur.rowcount
    cur.close()
    conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}
