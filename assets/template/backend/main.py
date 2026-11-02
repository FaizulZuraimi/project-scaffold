"""The {{PROJECT_NAME}} backend."""

from fastapi import FastAPI

app = FastAPI(title="{{PROJECT_NAME}}")


@app.get("/api/health", operation_id="health")
def health() -> dict[str, str]:
    """Check that the backend is running."""
    return {"status": "ok"}
