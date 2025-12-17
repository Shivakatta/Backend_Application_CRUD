from fastapi import FastAPI, HTTPException
from .routes.user_routes import router as user_router
from .routes.auth_routes import router as auth_router
from . import db
import os
import logging

# -------------------------
# Create FastAPI app
# -------------------------
app = FastAPI(title="User API", version="1.0")

# -------------------------
# Include user routes
# -------------------------
app.include_router(user_router)  # routes like /users, /users/{id}
app.include_router(auth_router)

# -------------------------
# Startup event: DB init
# -------------------------
@app.on_event("startup")
def startup():
    """
    Initialize the database on server startup,
    unless SKIP_DB_INIT=1 is set for dev/testing.
    """
    if os.environ.get("SKIP_DB_INIT") == "1":
        logging.info("SKIP_DB_INIT is set; skipping db.init_db()")
        return
    try:
        db.init_db()
        logging.info("Database initialized successfully")
    except Exception:
        logging.exception("db.init_db() failed during startup")

# -------------------------
# Root endpoint
# -------------------------
@app.get("/")
def root():
    """
    Returns basic server status and mock data from DB.
    """
    try:
        conn = db.get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM mock_data")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {"status": "Backend running", "data": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------
# Lightweight health endpoint
# -------------------------
@app.get("/health")
def health():
    """
    Simple health check without DB access.
    Useful to confirm server is running.
    """
    return {"status": "ok"}
