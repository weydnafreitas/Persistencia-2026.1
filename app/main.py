from __future__ import annotations
 
from fastapi import FastAPI
 
app = FastAPI(title="Gestão Hospitalar", version="1.0.0")
 
 
# from app.routers import medicos
# app.include_router(medicos.router)
 
 
@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Gestão Hospitalar"}
 