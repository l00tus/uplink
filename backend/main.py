from fastapi import FastAPI

app = FastAPI(title="Uplink")

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}