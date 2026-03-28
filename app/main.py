from fastapi import FastAPI

app = FastAPI(title="Gestão Hospitalar", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Gestão Hospitalar Delta Lake ✅"}