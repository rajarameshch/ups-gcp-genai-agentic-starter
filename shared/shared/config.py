from pydantic import BaseModel
import os

class Settings(BaseModel):
    service_name: str = "ups-genai"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

def get_settings() -> Settings:
    return Settings()
