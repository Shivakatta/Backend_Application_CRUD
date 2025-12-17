# Backend CRUD (FastAPI + MySQL)

Quick guide to run the small FastAPI CRUD app.

Prerequisites
- Python 3.8+
- MySQL server running on localhost
- Database user `root` with password `Shiva@366` (adjust in `db.py` if different)

Install

```bash
python -m pip install -r requirements.txt
```

Run

```bash
uvicorn backend.main:app --reload
```

API endpoints (default base '/')
- `GET /users` — list users
- `POST /users` — create user (JSON body: `{"name":"...","email":"..."}`)
- `PUT /users/{id}` — full update (same JSON as POST)
- `PATCH /users/{id}` — partial update (any of `name` or `email`)
- `DELETE /users/{id}` — delete user

If your DB credentials or host differ, edit `db.py`.
