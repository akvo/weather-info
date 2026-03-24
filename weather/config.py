"""Configuration management - loads API keys from .env file."""

import os
from pathlib import Path

from dotenv import load_dotenv


def load_config() -> None:
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)


def get_openweather_api_key() -> str:
    """Get OpenWeatherMap API key from environment."""
    load_config()
    key = os.getenv("OPENWEATHER")
    if not key:
        raise ValueError("OPENWEATHER API key not found in .env file")
    return key


def get_weatherapi_key() -> str:
    """Get WeatherAPI.com API key from environment."""
    load_config()
    key = os.getenv("WEATHERAPI")
    if not key:
        raise ValueError("WEATHERAPI API key not found in .env file")
    return key


def get_google_weather_key() -> str:
    """Get Google Maps Weather API key from environment."""
    load_config()
    key = os.getenv("GOOGLEWEATHER")
    if not key:
        raise ValueError("GOOGLEWEATHER API key not found in .env file")
    return key
