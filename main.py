from fastapi import FastAPI

app = FastAPI(title="Payment System")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
