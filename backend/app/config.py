"""
Configuration loaded from environment variables.

Never hardcode connection details here. Copy .env.example to .env at the
repo root and fill in the values you got from console.cognodb.com.
"""
import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))


class Settings:
    COGNODB_URI: str = os.getenv("COGNODB_URI", "")
    COGNODB_USER: str = os.getenv("COGNODB_USER", "cognodb")
    COGNODB_PASSWORD: str = os.getenv("COGNODB_PASSWORD", "")
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5174"
    ).split(",")


settings = Settings()
