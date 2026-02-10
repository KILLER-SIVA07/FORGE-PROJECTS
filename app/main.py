from fastapi import FastAPI

from app.db import Base, engine
from app.routers import auth, events, gate, registrations

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Enterprise QR Visitor Management API", version="3.0.0")

app.include_router(auth.router)
app.include_router(events.router)
app.include_router(registrations.router)
app.include_router(gate.router)


@app.get("/health")
def health():
    return {"status": "ok"}
