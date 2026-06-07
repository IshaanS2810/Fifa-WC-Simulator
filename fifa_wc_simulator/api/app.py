import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="FIFA World Cup Simulator API",
    version="0.1.0"
)
print("CORS APP LOADED SUCCESSFULLY")

# ==========================================
# CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# ROUTES
# ==========================================

app.include_router(router)

# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
def health_check() -> dict:
    """Health check endpoint for the API."""
    return {"status": "ok"}