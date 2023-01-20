from fastapi import APIRouter

app = APIRouter()


@app.get("/")
async def get_status():
    return {"status": 200}
