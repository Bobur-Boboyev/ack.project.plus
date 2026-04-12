from fastapi import FastAPI

from app.db.init_db import create_tables


create_tables()


app = FastAPI(title="Ack Project")


@app.get("/")
async def health_check():
    return {"message": "ok"}
