from pydantic_settings import BaseSettings
from pydantic import ConfigDict, validator, Field
from typing import Optional, Literal
import os
from pathlib import Path

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Allow extra fields in .env file
        case_sensitive=False  # Allow case-insensitive env var matching
    )

    # API Configuration
    API_V1_STR: str = "/api/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    
    # Exness Broker Configuration
    EXNESS_LOGIN: str = Field(..., description="Exness account login")
    EXNESS_PASSWORD: str = Field(..., description="Exness account password")
    EXNESS_SERVER: str = Field(..., description="Exness server (e.g., Exness-MT5Trial8)")
    EXNESS_ACCOUNT_TYPE: Literal["demo", "live"] = "demo"
    EXNESS_TERMINAL: Literal["MT4", "MT5"] = "MT5"
    
    # Trading Configuration
    MT5_SYMBOL: str = "XAUUSD"
    MT5_TIMEFRAME: str = "TIMEFRAME_M15"
    EA_MAGIC_NUMBER: int = 12345
    EA_DEFAULT_LOT_SIZE: float = 0.01
    EA_MAX_RISK_PER_TRADE: float = 0.02  # 2% risk per trade
    
    # EA Communication
    EA_SERVER_HOST: str = "localhost"
    EA_SERVER_PORT: int = 5000
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://genx:password@localhost:5432/genx_trading"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = Field(..., description="Secret key for JWT tokens")
    ALGORITHM: str = "HS256"  # SECURITY: Explicitly set JWT algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # SECURITY: Additional security settings
    REQUIRE_HTTPS: bool = True  # Force HTTPS in production
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]  # Restrict CORS
    MAX_LOGIN_ATTEMPTS: int = 5  # Rate limiting
    LOCKOUT_DURATION_MINUTES: int = 15
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/var/log/genx-trading/app.log"
    
    # VPS Configuration
    VPS_PUBLIC_IP: Optional[str] = None
    
    @validator('EXNESS_LOGIN')
    def validate_login(cls, v):
        if not v or len(v) < 6:
            raise ValueError('Login must be at least 6 characters')
        return v
    
    @validator('EXNESS_PASSWORD')
    def validate_password(cls, v):
        if not v or len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
    
    @validator('EA_DEFAULT_LOT_SIZE')
    def validate_lot_size(cls, v):
        if v <= 0 or v > 100:
            raise ValueError('Lot size must be between 0.01 and 100')
        return v
    
    @validator('EA_MAX_RISK_PER_TRADE')
    def validate_risk_percentage(cls, v):
        if v <= 0 or v > 0.1:  # Max 10% risk per trade
            raise ValueError('Risk per trade must be between 0.01 and 0.1 (1-10%)')
        return v
    
    def get_database_url(self) -> str:
        """Get database URL with proper formatting"""
        return self.DATABASE_URL
    
    def get_redis_url(self) -> str:
        """Get Redis URL with proper formatting"""
        return self.REDIS_URL
    
    def is_demo_account(self) -> bool:
        """Check if using demo account"""
        return self.EXNESS_ACCOUNT_TYPE.lower() == "demo"
    
    def get_ea_connection_string(self) -> str:
        """Get EA connection string for socket communication"""
        return f"{self.EA_SERVER_HOST}:{self.EA_SERVER_PORT}"

# Create global settings instance
settings = Settings()

# Optional: Environment-specific settings
class DevelopmentSettings(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

class ProductionSettings(Settings):
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"

# Factory function to get appropriate settings
def get_settings() -> Settings:
    env = os.getenv("ENVIRONMENT", "development").lower()
    if env == "production":
        return ProductionSettings()
    return DevelopmentSettings()
