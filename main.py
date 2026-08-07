from fastapi import FastAPI

from app.api import api_router

app = FastAPI(title="Payment System")
app.include_router(api_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
