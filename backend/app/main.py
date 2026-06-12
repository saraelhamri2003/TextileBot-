import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import engine, Base
from backend.app.api import auth, documents, chat, compliance, fine_tuned_models
import backend.app.models.fine_tuned_model  # ensure SQLAlchemy model is imported for metadata registration

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Create tables in SQLite (simple migrations)
try:
    logger.info("Initializing SQLite tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized.")
except Exception as e:
    logger.error(f"Failed to initialize database tables: {str(e)}")

app = FastAPI(
    title="TextilBot API",
    description="Assistant de conformité réglementaire textile RAG",
    version="1.0.0"
)

# CORS Configuration for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth, prefix="/api/v1")
app.include_router(documents, prefix="/api/v1")
app.include_router(chat, prefix="/api/v1")
app.include_router(compliance, prefix="/api/v1")
app.include_router(fine_tuned_models, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "TextilBot API Service",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
