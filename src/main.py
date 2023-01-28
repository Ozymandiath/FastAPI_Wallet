from fastapi import FastAPI

from src.auth.router import router as router_auth

app = FastAPI()

app.include_router(router_auth, prefix="/user", tags=["Authentication"])


