import os
from pathlib import Path
from typing import Dict, List, Any, Optional

from pydantic import BaseSettings
from pydantic.env_settings import SettingsSourceCallable
from dotenv import load_dotenv

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent.parent

def load_env_file() -> None:
    """
    Loads environment variables from .env file based on the current environment.
    
    Prioritizes environment-specific .env files (e.g., .env.development, .env.production)
    and falls back to .env if the specific file doesn't exist.
    """
    # Determine the environment (development, staging, production)
    env = os.getenv("ENV", "development").lower()
    
    # Construct paths to potential .env files
    env_file_specific = BASE_DIR / f".env.{env}"
    env_file_default = BASE_DIR / ".env"
    
    # Try to load the environment-specific file first, then fall back to default
    if env_file_specific.exists():
        load_dotenv(env_file_specific)
        print(f"Loaded environment variables from {env_file_specific}")
    elif env_file_default.exists():
        load_dotenv(env_file_default)
        print(f"Loaded environment variables from {env_file_default}")
    else:
        print("No .env file found. Using environment variables directly.")
    
    print(f"Running in {env} environment")

class Settings(BaseSettings):
    """
    Pydantic settings class that manages all application configuration.
    
    This class centralizes all configuration parameters, including database
    connections, cache settings, security credentials, and application metadata.
    It loads values from environment variables and provides validation and type checking.
    """
    # Application metadata
    ENV: str = "development"
    APP_NAME: str = "Freight Price Movement Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API settings
    API_PREFIX: str = "/api/v1"
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/freight_agent"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Cache TTL settings (in seconds)
    CACHE_TTL: int = 3600  # 1 hour
    RESULT_CACHE_TTL: int = 3600  # 1 hour
    REFERENCE_CACHE_TTL: int = 86400  # 24 hours
    QUERY_CACHE_TTL: int = 900  # 15 minutes
    
    # Security settings
    JWT_SECRET_KEY: str = "super-secret-key-replace-in-production"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Monitoring settings
    SENTRY_DSN: Optional[str] = None
    
    class Config:
        """Pydantic configuration class for Settings."""
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"
    
    def __init__(self, *args, **kwargs):
        """
        Initializes the Settings class with default values and environment variables.
        
        Loads environment variables from .env file before initializing the settings.
        """
        # Load environment variables from .env file
        load_env_file()
        super().__init__(*args, **kwargs)
    
    def get_database_connection_parameters(self) -> Dict[str, Any]:
        """
        Constructs database connection parameters from settings.
        
        Returns:
            dict: Dictionary with database connection parameters
        """
        # Extract database URL components and construct connection parameters
        # In a real implementation, we would parse the DATABASE_URL
        return {
            "host": os.environ.get("DB_HOST", "localhost"),
            "port": int(os.environ.get("DB_PORT", "5432")),
            "username": os.environ.get("DB_USER", "postgres"),
            "password": os.environ.get("DB_PASSWORD", "postgres"),
            "database": os.environ.get("DB_NAME", "freight_agent"),
            "pool_size": self.DATABASE_POOL_SIZE,
            "max_overflow": self.DATABASE_MAX_OVERFLOW,
            "sslmode": os.environ.get("DB_SSL_MODE", "prefer")
        }
    
    def get_redis_connection_parameters(self) -> Dict[str, Any]:
        """
        Constructs Redis connection parameters from settings.
        
        Returns:
            dict: Dictionary with Redis connection parameters
        """
        # Extract Redis URL components and construct connection parameters
        # In a real implementation, we would parse the REDIS_URL
        return {
            "host": os.environ.get("REDIS_HOST", "localhost"),
            "port": int(os.environ.get("REDIS_PORT", "6379")),
            "password": os.environ.get("REDIS_PASSWORD", None),
            "db": int(os.environ.get("REDIS_DB", "0")),
            "ssl": os.environ.get("REDIS_SSL", "False").lower() == "true"
        }

# Create a global settings object to be imported by other modules
settings = Settings()