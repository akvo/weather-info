"""Base class for weather services."""

from abc import ABC, abstractmethod

from weather.models import WeatherData, Forecast


class WeatherService(ABC):
    """Abstract base class for weather service providers."""

    @abstractmethod
    def get_current(self, location: str) -> WeatherData:
        """Get current weather for a location."""
        pass

    @abstractmethod
    def get_forecast_hourly(self, location: str, hours: int = 24) -> list[Forecast]:
        """Get hourly forecast for a location."""
        pass

    @abstractmethod
    def get_forecast_daily(self, location: str, days: int = 7) -> list[Forecast]:
        """Get daily forecast for a location."""
        pass

    @abstractmethod
    def get_current_raw(self, location: str) -> dict:
        """Get raw API response for current weather."""
        pass

    @abstractmethod
    def get_forecast_raw(self, location: str) -> dict:
        """Get raw API response for forecast."""
        pass
