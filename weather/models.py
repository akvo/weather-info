"""Data models for weather data."""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class WeatherData:
    """Current weather data."""

    location: str
    temperature: float  # Celsius
    feels_like: float  # Celsius
    humidity: int  # Percentage
    description: str
    wind_speed: float  # m/s
    timestamp: datetime

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class Forecast(WeatherData):
    """Forecast weather data with forecast time."""

    forecast_time: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = super().to_dict()
        if self.forecast_time:
            data["forecast_time"] = self.forecast_time.isoformat()
        return data
