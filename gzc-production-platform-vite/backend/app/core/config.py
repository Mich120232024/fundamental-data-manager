import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GZC Production Platform"
    VERSION: str = "1.0.0"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3200",
        "https://platform.gzc.com"
    ]
    
    # Azure Key Vault Configuration
    KEY_VAULT_URL: str = "https://gzc-finma-keyvault.vault.azure.net/"
    
    # Database Configuration (will be loaded from Key Vault)
    DATABASE_URL: str = ""
    
    # Redis Configuration (will be loaded from Key Vault)
    REDIS_URL: str = ""
    
    # Azure Configuration
    AZURE_CLIENT_ID: str = os.getenv("AZURE_CLIENT_ID", "")
    AZURE_TENANT_ID: str = os.getenv("AZURE_TENANT_ID", "")
    
    # WebSocket Configuration
    WEBSOCKET_URL: str = os.getenv("WEBSOCKET_URL", "ws://localhost:8000/ws")
    ESP_WEBSOCKET_URL: str = os.getenv("ESP_WEBSOCKET_URL", "ws://localhost:8001/esp")
    RFS_WEBSOCKET_URL: str = os.getenv("RFS_WEBSOCKET_URL", "ws://localhost:8002/rfs")
    
    # Cache Configuration
    CACHE_TTL: int = 300  # 5 minutes
    QUOTES_CACHE_TTL: int = 30  # 30 seconds for live quotes
    
    class Config:
        env_file = ".env"


settings = Settings()