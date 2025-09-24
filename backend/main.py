from fastapi import FastAPI
from .routes.user import router as user_router

app = FastAPI(title="Uplink")

app.include_router(user_router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}