from fastapi import FastAPI
from .routes.user import router as user_router
from .routes.auth import router as auth_router

app = FastAPI(title="Uplink")

app.include_router(user_router)
app.include_router(auth_router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}