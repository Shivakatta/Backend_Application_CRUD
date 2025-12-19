from fastapi import FastAPI
from backend.routes import auth_routes, user_routes

app = FastAPI()

app.include_router(auth_routes.router)
app.include_router(user_routes.router)

@app.get("/")
def root():
    return {"message": "API is running"}
