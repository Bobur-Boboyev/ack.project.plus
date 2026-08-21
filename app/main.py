from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.db.init_db import create_tables, drop_tables

# drop_tables()
# create_tables()

app = FastAPI(title="Ack Project")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(router)


@app.get("/")
def health_check():
    return {"message": "ok"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Keyinchalik netlify domeningizni yoziladi
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)