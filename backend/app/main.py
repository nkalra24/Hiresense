import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base
import app.models  # Ensure all models are registered
from app.api import screenings, candidates, settings as settings_api, health
from app.ml.similarity_engine import similarity_engine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("hiresense")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and trigger AI model warm up
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info(f"AI Engine status: {similarity_engine.is_model_loaded} (Model: {settings.EMBEDDING_MODEL_NAME})")
    yield
    # Shutdown
    logger.info("Shutting down HireSense AI backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent, explainable, and multi-signal resume screening and candidate ranking engine.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers under /api
app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(screenings.router, prefix=settings.API_PREFIX)
app.include_router(candidates.router, prefix=settings.API_PREFIX)
app.include_router(settings_api.router, prefix=settings.API_PREFIX)

@app.get("/")
def root_redirect():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_check": f"{settings.API_PREFIX}/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
