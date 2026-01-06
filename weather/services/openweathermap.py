"""OpenWeatherMap service implementation."""

from datetime import datetime

import httpx

from weather.config import get_openweather_api_key
from weather.models import WeatherData, Forecast
from weather.services.base import WeatherService


class OpenWeatherMapService(WeatherService):
    """OpenWeatherMap API service."""

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self):
        self.api_key = get_openweather_api_key()
        self.client = httpx.Client(timeout=30.0)

    def get_current(self, location: str) -> WeatherData:
        """Get current weather for a location."""
        url = f"{self.BASE_URL}/weather"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric",
        }
        response = self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        return WeatherData(
            location=f"{data['name']}, {data['sys']['country']}",
            temperature=data["main"]["temp"],
            feels_like=data["main"]["feels_like"],
            humidity=data["main"]["humidity"],
            description=data["weather"][0]["description"],
            wind_speed=data["wind"]["speed"],
            timestamp=datetime.fromtimestamp(data["dt"]),
        )

    def get_forecast_hourly(self, location: str, hours: int = 24) -> list[Forecast]:
        """Get hourly forecast (3-hour intervals from OWM free API)."""
        url = f"{self.BASE_URL}/forecast"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric",
        }
        response = self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        forecasts = []
        # OWM free API provides 3-hour intervals, limit by hours/3
        max_items = hours // 3
        for item in data["list"][:max_items]:
            forecast = Forecast(
                location=f"{data['city']['name']}, {data['city']['country']}",
                temperature=item["main"]["temp"],
                feels_like=item["main"]["feels_like"],
                humidity=item["main"]["humidity"],
                description=item["weather"][0]["description"],
                wind_speed=item["wind"]["speed"],
                timestamp=datetime.now(),
                forecast_time=datetime.fromtimestamp(item["dt"]),
            )
            forecasts.append(forecast)

        return forecasts

    def get_forecast_daily(self, location: str, days: int = 7) -> list[Forecast]:
        """Get daily forecast (approximated from 3-hour forecast)."""
        url = f"{self.BASE_URL}/forecast"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric",
        }
        response = self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Group by date and take midday forecast (12:00)
        daily_forecasts = {}
        for item in data["list"]:
            dt = datetime.fromtimestamp(item["dt"])
            date_key = dt.date()
            # Prefer midday forecast or first available
            if date_key not in daily_forecasts or dt.hour == 12:
                daily_forecasts[date_key] = item

        forecasts = []
        for date_key, item in list(daily_forecasts.items())[:days]:
            forecast = Forecast(
                location=f"{data['city']['name']}, {data['city']['country']}",
                temperature=item["main"]["temp"],
                feels_like=item["main"]["feels_like"],
                humidity=item["main"]["humidity"],
                description=item["weather"][0]["description"],
                wind_speed=item["wind"]["speed"],
                timestamp=datetime.now(),
                forecast_time=datetime.fromtimestamp(item["dt"]),
            )
            forecasts.append(forecast)

        return forecasts

    def get_current_raw(self, location: str) -> dict:
        """Get raw API response for current weather."""
        url = f"{self.BASE_URL}/weather"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric",
        }
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_forecast_raw(self, location: str) -> dict:
        """Get raw API response for forecast."""
        url = f"{self.BASE_URL}/forecast"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric",
        }
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
