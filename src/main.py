from fastapi import FastAPI

from auth.router import app as auth_app

app = FastAPI()

# app.include_router(auth_app, prefix="/auth", tags=["Authorization"])


