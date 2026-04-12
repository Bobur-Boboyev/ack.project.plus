from fastapi import FastAPI

from app.api import router
from app.db.init_db import create_tables


# create_tables()


app = FastAPI(title="Ack Project")

app.include_router(router)


@app.get("/")
async def health_check():
    return {"message": "ok"}
