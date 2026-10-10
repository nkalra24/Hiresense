import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "HireSense AI — Intelligent Resume Screening & Ranking System"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Base Directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    
    # Database (SQLite by default for zero-config local run, switchable to PostgreSQL via env)
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'hiresense.db'}")
    
    # AI / Embedding Model
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    USE_GPU: bool = os.getenv("USE_GPU", "false").lower() in ("true", "1")
    
    # Scoring Defaults (Percentages summing to 100)
    DEFAULT_WEIGHT_REQUIRED_SKILLS: float = 35.0
    DEFAULT_WEIGHT_SEMANTIC_SIMILARITY: float = 25.0
    DEFAULT_WEIGHT_EXPERIENCE: float = 20.0
    DEFAULT_WEIGHT_PREFERRED_SKILLS: float = 10.0
    DEFAULT_WEIGHT_EDUCATION: float = 10.0
    
    # Overqualification Thresholds (years in excess)
    OVERQUALIFICATION_EXP_THRESHOLD_YEARS: float = 4.0
    
    # File Limits
    MAX_FILE_SIZE_BYTES: int = 15 * 1024 * 1024  # 15MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx"}
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

# Ensure uploads directory exists
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
