"""WeatherAPI.com service implementation."""

from datetime import datetime

import httpx

from weather.config import get_weatherapi_key
from weather.models import WeatherData, Forecast
from weather.services.base import WeatherService


class WeatherAPIService(WeatherService):
    """WeatherAPI.com API service."""

    BASE_URL = "https://api.weatherapi.com/v1"

    def __init__(self):
        self.api_key = get_weatherapi_key()
        self.client = httpx.Client(timeout=30.0)

    def get_current(self, location: str) -> WeatherData:
        """Get current weather for a location."""
        url = f"{self.BASE_URL}/current.json"
        params = {
            "key": self.api_key,
            "q": location,
        }
        response = self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        return WeatherData(
            location=f"{data['location']['name']}, {data['location']['country']}",
            temperature=data["current"]["temp_c"],
            feels_like=data["current"]["feelslike_c"],
            humidity=data["current"]["humidity"],
            description=data["current"]["condition"]["text"],
            wind_speed=data["current"]["wind_kph"] / 3.6,  # Convert to m/s
            timestamp=datetime.fromtimestamp(data["current"]["last_updated_epoch"]),
        )

    def get_forecast_hourly(self, location: str, hours: int = 24) -> list[Forecast]:
        """Get hourly forecast for a location."""
        # WeatherAPI free tier allows up to 3 days
        days = min((hours // 24) + 1, 3)
        url = f"{self.BASE_URL}/forecast.json"
        params = {
            "key": self.api_key,
            "q": location,
            "days": days,
        }
        response = self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        forecasts = []
        location_str = f"{data['location']['name']}, {data['location']['country']}"
        now = datetime.now()

        for day in data["forecast"]["forecastday"]:
            for hour_data in day["hour"]:
                hour_dt = datetime.fromtimestamp(hour_data["time_epoch"])
                if hour_dt > now and len(forecasts) < hours:
                    forecast = Forecast(
                        location=location_str,
                        temperature=hour_data["temp_c"],
                        feels_like=hour_data["feelslike_c"],
                        humidity=hour_data["humidity"],
                        description=hour_data["condition"]["text"],
                        wind_speed=hour_data["wind_kph"] / 3.6,
                        timestamp=now,
                        forecast_time=hour_dt,
                    )
                    forecasts.append(forecast)

        return forecasts

    def get_forecast_daily(self, location: str, days: int = 7) -> list[Forecast]:
        """Get daily forecast for a location."""
        # WeatherAPI free tier allows up to 3 days
        days = min(days, 3)
        url = f"{self.BASE_URL}/forecast.json"
        params = {
            "key": self.api_key,
            "q": location,
            "days": days,
        }
        response = self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        forecasts = []
        location_str = f"{data['location']['name']}, {data['location']['country']}"
        now = datetime.now()

        for day in data["forecast"]["forecastday"]:
            day_data = day["day"]
            forecast = Forecast(
                location=location_str,
                temperature=day_data["avgtemp_c"],
                feels_like=day_data["avgtemp_c"],  # No feels_like for daily
                humidity=day_data["avghumidity"],
                description=day_data["condition"]["text"],
                wind_speed=day_data["maxwind_kph"] / 3.6,
                timestamp=now,
                forecast_time=datetime.strptime(day["date"], "%Y-%m-%d"),
            )
            forecasts.append(forecast)

        return forecasts

    def get_current_raw(self, location: str) -> dict:
        """Get raw API response for current weather."""
        url = f"{self.BASE_URL}/current.json"
        params = {
            "key": self.api_key,
            "q": location,
        }
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_forecast_raw(self, location: str) -> dict:
        """Get raw API response for forecast."""
        url = f"{self.BASE_URL}/forecast.json"
        params = {
            "key": self.api_key,
            "q": location,
            "days": 3,
        }
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
