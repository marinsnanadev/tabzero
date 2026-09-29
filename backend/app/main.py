from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import sessions

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Rachômetro API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
