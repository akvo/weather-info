"""Google Maps Weather API service implementation."""

from datetime import datetime
from typing import Optional

import httpx

from weather.config import get_google_weather_key
from weather.models import WeatherData, Forecast
from weather.services.base import WeatherService


class GoogleWeatherService(WeatherService):
    """Google Maps Platform Weather API service.

    Uses Google's Weather API which requires coordinates (lat/lon).
    Location strings are geocoded using Google's Geocoding API.

    Example:
        service = GoogleWeatherService()

        # Location-based queries (geocoded automatically)
        data = service.get_current("Jakarta, Indonesia")
        forecast = service.get_forecast_hourly("London, UK", hours=24)

        # Coordinate-based queries (no geocoding)
        data = service.get_current_by_coords(lat=-6.2088, lon=106.8456)
        raw = service.get_current_raw_by_coords(lat=51.5074, lon=-0.1278)
    """

    WEATHER_URL = "https://weather.googleapis.com/v1"
    GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

    def __init__(self):
        self.api_key = get_google_weather_key()
        self.client = httpx.Client(timeout=30.0)
        self._geocode_cache: dict[str, tuple[float, float, str]] = {}

    def _geocode(self, location: str) -> tuple[float, float, str]:
        """Convert location string to coordinates.

        Returns:
            Tuple of (latitude, longitude, formatted_address)
        """
        if location in self._geocode_cache:
            return self._geocode_cache[location]

        response = self.client.get(
            self.GEOCODE_URL,
            params={"address": location, "key": self.api_key},
        )
        response.raise_for_status()
        data = response.json()

        if data["status"] != "OK" or not data.get("results"):
            raise ValueError(f"Could not geocode location: {location}")

        result = data["results"][0]
        lat = result["geometry"]["location"]["lat"]
        lon = result["geometry"]["location"]["lng"]
        formatted_address = result["formatted_address"]

        self._geocode_cache[location] = (lat, lon, formatted_address)
        return lat, lon, formatted_address

    def get_current(self, location: str) -> WeatherData:
        """Get current weather for a location."""
        lat, lon, address = self._geocode(location)

        response = self.client.get(
            f"{self.WEATHER_URL}/currentConditions:lookup",
            params={
                "key": self.api_key,
                "location.latitude": lat,
                "location.longitude": lon,
            },
        )
        response.raise_for_status()
        data = response.json()

        # Extract wind speed (convert km/h to m/s if needed)
        wind_speed = 0.0
        if "wind" in data and "speed" in data["wind"]:
            wind_data = data["wind"]["speed"]
            wind_speed = wind_data.get("value", 0)
            if wind_data.get("unit") in ("km/h", "KILOMETERS_PER_HOUR"):
                wind_speed = wind_speed / 3.6

        return WeatherData(
            location=address,
            temperature=data.get("temperature", {}).get("degrees", 0),
            feels_like=data.get("feelsLikeTemperature", {}).get("degrees", 0),
            humidity=data.get("relativeHumidity", 0),
            description=data.get("weatherCondition", {})
            .get("description", {})
            .get("text", ""),
            wind_speed=wind_speed,
            timestamp=datetime.now(),
        )

    def get_forecast_hourly(self, location: str, hours: int = 24) -> list[Forecast]:
        """Get hourly forecast for a location."""
        lat, lon, address = self._geocode(location)

        response = self.client.get(
            f"{self.WEATHER_URL}/forecast/hours:lookup",
            params={
                "key": self.api_key,
                "location.latitude": lat,
                "location.longitude": lon,
                "hours": min(hours, 240),  # API max is 240 hours
            },
        )
        response.raise_for_status()
        data = response.json()

        forecasts = []
        for hour_data in data.get("forecastHours", [])[:hours]:
            # Parse forecast time from interval
            interval = hour_data.get("interval", {})
            start_time = interval.get("startTime", "")
            forecast_time = None
            if start_time:
                forecast_time = datetime.fromisoformat(
                    start_time.replace("Z", "+00:00")
                )

            # Extract wind speed
            wind_speed = 0.0
            if "wind" in hour_data and "speed" in hour_data["wind"]:
                wind_data = hour_data["wind"]["speed"]
                wind_speed = wind_data.get("value", 0)
                if wind_data.get("unit") in ("km/h", "KILOMETERS_PER_HOUR"):
                    wind_speed = wind_speed / 3.6

            forecast = Forecast(
                location=address,
                temperature=hour_data.get("temperature", {}).get("degrees", 0),
                feels_like=hour_data.get("feelsLikeTemperature", {}).get("degrees", 0),
                humidity=hour_data.get("relativeHumidity", 0),
                description=hour_data.get("weatherCondition", {})
                .get("description", {})
                .get("text", ""),
                wind_speed=wind_speed,
                timestamp=datetime.now(),
                forecast_time=forecast_time,
            )
            forecasts.append(forecast)

        return forecasts

    def get_forecast_daily(self, location: str, days: int = 7) -> list[Forecast]:
        """Get daily forecast for a location."""
        lat, lon, address = self._geocode(location)

        response = self.client.get(
            f"{self.WEATHER_URL}/forecast/days:lookup",
            params={
                "key": self.api_key,
                "location.latitude": lat,
                "location.longitude": lon,
                "days": min(days, 10),  # API max is 10 days
            },
        )
        response.raise_for_status()
        data = response.json()

        forecasts = []
        for day_data in data.get("forecastDays", [])[:days]:
            # Parse date from interval or displayDate
            interval = day_data.get("interval", {})
            start_time = interval.get("startTime", "")
            forecast_time = None
            if start_time:
                forecast_time = datetime.fromisoformat(
                    start_time.replace("Z", "+00:00")
                )

            # Use daytime conditions if available, otherwise overall
            daytime = day_data.get("daytimeForecast", day_data)

            # Extract wind speed
            wind_speed = 0.0
            if "wind" in daytime and "speed" in daytime["wind"]:
                wind_data = daytime["wind"]["speed"]
                wind_speed = wind_data.get("value", 0)
                if wind_data.get("unit") in ("km/h", "KILOMETERS_PER_HOUR"):
                    wind_speed = wind_speed / 3.6

            # Get temperature (prefer max for daily)
            temp = daytime.get("temperature", {}).get("degrees", 0)
            if "maxTemperature" in day_data:
                temp = day_data["maxTemperature"].get("degrees", temp)

            forecast = Forecast(
                location=address,
                temperature=temp,
                feels_like=daytime.get("feelsLikeTemperature", {}).get("degrees", temp),
                humidity=daytime.get("relativeHumidity", 0),
                description=daytime.get("weatherCondition", {})
                .get("description", {})
                .get("text", ""),
                wind_speed=wind_speed,
                timestamp=datetime.now(),
                forecast_time=forecast_time,
            )
            forecasts.append(forecast)

        return forecasts

    def get_current_raw(self, location: str) -> dict:
        """Get raw API response for current weather."""
        lat, lon, _ = self._geocode(location)

        response = self.client.get(
            f"{self.WEATHER_URL}/currentConditions:lookup",
            params={
                "key": self.api_key,
                "location.latitude": lat,
                "location.longitude": lon,
            },
        )
        response.raise_for_status()
        return response.json()

    def get_forecast_raw(self, location: str) -> dict:
        """Get raw API response for forecast (hourly)."""
        lat, lon, _ = self._geocode(location)

        response = self.client.get(
            f"{self.WEATHER_URL}/forecast/hours:lookup",
            params={
                "key": self.api_key,
                "location.latitude": lat,
                "location.longitude": lon,
            },
        )
        response.raise_for_status()
        return response.json()

    def get_daily_forecast_raw(
        self, location: str, days: int = 10
    ) -> dict:
        """Get raw API response for daily forecast.

        Args:
            location: Location string to get forecast for.
            days: Number of days (max 10).

        Returns:
            Raw JSON response from the daily forecast API.
        """
        lat, lon, _ = self._geocode(location)
        return self.get_daily_forecast_raw_by_coords(lat, lon, days)

    # -------------------------------------------------------------------------
    # Coordinate-based methods (no geocoding required)
    # -------------------------------------------------------------------------

    def _extract_wind_speed(self, data: dict) -> float:
        """Extract wind speed from API response and convert to m/s."""
        wind_speed = 0.0
        if "wind" in data and "speed" in data["wind"]:
            wind_data = data["wind"]["speed"]
            wind_speed = wind_data.get("value", 0)
            if wind_data.get("unit") in ("km/h", "KILOMETERS_PER_HOUR"):
                wind_speed = wind_speed / 3.6
        return wind_speed

    def get_current_by_coords(
        self, lat: float, lon: float, location_name: Optional[str] = None
    ) -> WeatherData:
        """Get current weather by coordinates.

        Args:
            lat: Latitude of the location.
            lon: Longitude of the location.
            location_name: Optional display name for the location.

        Returns:
            WeatherData object with current conditions.
        """
        data = self.get_current_raw_by_coords(lat, lon)
        address = location_name or f"{lat}, {lon}"

        return WeatherData(
            location=address,
            temperature=data.get("temperature", {}).get("degrees", 0),
            feels_like=data.get("feelsLikeTemperature", {}).get("degrees", 0),
            humidity=data.get("relativeHumidity", 0),
            description=data.get("weatherCondition", {})
            .get("description", {})
            .get("text", ""),
            wind_speed=self._extract_wind_speed(data),
            timestamp=datetime.now(),
        )

    def get_forecast_hourly_by_coords(
        self,
        lat: float,
        lon: float,
        hours: int = 24,
        location_name: Optional[str] = None,
    ) -> list[Forecast]:
        """Get hourly forecast by coordinates.

        Args:
            lat: Latitude of the location.
            lon: Longitude of the location.
            hours: Number of hours to forecast (max 240).
            location_name: Optional display name for the location.

        Returns:
            List of Forecast objects.
        """
        data = self.get_forecast_raw_by_coords(lat, lon, hours)
        address = location_name or f"{lat}, {lon}"

        forecasts = []
        for hour_data in data.get("forecastHours", [])[:hours]:
            interval = hour_data.get("interval", {})
            start_time = interval.get("startTime", "")
            forecast_time = None
            if start_time:
                forecast_time = datetime.fromisoformat(
                    start_time.replace("Z", "+00:00")
                )

            forecast = Forecast(
                location=address,
                temperature=hour_data.get("temperature", {}).get("degrees", 0),
                feels_like=hour_data.get("feelsLikeTemperature", {}).get("degrees", 0),
                humidity=hour_data.get("relativeHumidity", 0),
                description=hour_data.get("weatherCondition", {})
                .get("description", {})
                .get("text", ""),
                wind_speed=self._extract_wind_speed(hour_data),
                timestamp=datetime.now(),
                forecast_time=forecast_time,
            )
            forecasts.append(forecast)

        return forecasts

    def get_forecast_daily_by_coords(
        self,
        lat: float,
        lon: float,
        days: int = 7,
        location_name: Optional[str] = None,
    ) -> list[Forecast]:
        """Get daily forecast by coordinates.

        Args:
            lat: Latitude of the location.
            lon: Longitude of the location.
            days: Number of days to forecast (max 10).
            location_name: Optional display name for the location.

        Returns:
            List of Forecast objects.
        """
        data = self.get_daily_forecast_raw_by_coords(lat, lon, days)
        address = location_name or f"{lat}, {lon}"

        forecasts = []
        for day_data in data.get("forecastDays", [])[:days]:
            interval = day_data.get("interval", {})
            start_time = interval.get("startTime", "")
            forecast_time = None
            if start_time:
                forecast_time = datetime.fromisoformat(
                    start_time.replace("Z", "+00:00")
                )

            daytime = day_data.get("daytimeForecast", day_data)
            temp = daytime.get("temperature", {}).get("degrees", 0)
            if "maxTemperature" in day_data:
                temp = day_data["maxTemperature"].get("degrees", temp)

            forecast = Forecast(
                location=address,
                temperature=temp,
                feels_like=daytime.get("feelsLikeTemperature", {}).get("degrees", temp),
                humidity=daytime.get("relativeHumidity", 0),
                description=daytime.get("weatherCondition", {})
                .get("description", {})
                .get("text", ""),
                wind_speed=self._extract_wind_speed(daytime),
                timestamp=datetime.now(),
                forecast_time=forecast_time,
            )
            forecasts.append(forecast)

        return forecasts

    def get_current_raw_by_coords(self, lat: float, lon: float) -> dict:
        """Get raw API response for current weather by coordinates.

        Args:
            lat: Latitude of the location.
            lon: Longitude of the location.

        Returns:
            Raw JSON response from the current conditions API.
        """
        response = self.client.get(
            f"{self.WEATHER_URL}/currentConditions:lookup",
            params={
                "key": self.api_key,
                "location.latitude": lat,
                "location.longitude": lon,
            },
        )
        response.raise_for_status()
        return response.json()

    def get_forecast_raw_by_coords(
        self, lat: float, lon: float, hours: int = 24
    ) -> dict:
        """Get raw API response for hourly forecast by coordinates.

        Args:
            lat: Latitude of the location.
            lon: Longitude of the location.
            hours: Number of hours to forecast (max 240).

        Returns:
            Raw JSON response from the hourly forecast API.
        """
        response = self.client.get(
            f"{self.WEATHER_URL}/forecast/hours:lookup",
            params={
                "key": self.api_key,
                "location.latitude": lat,
                "location.longitude": lon,
                "hours": min(hours, 240),
            },
        )
        response.raise_for_status()
        return response.json()

    def get_daily_forecast_raw_by_coords(
        self, lat: float, lon: float, days: int = 10
    ) -> dict:
        """Get raw API response for daily forecast by coordinates.

        Args:
            lat: Latitude of the location.
            lon: Longitude of the location.
            days: Number of days to forecast (max 10).

        Returns:
            Raw JSON response from the daily forecast API.
        """
        response = self.client.get(
            f"{self.WEATHER_URL}/forecast/days:lookup",
            params={
                "key": self.api_key,
                "location.latitude": lat,
                "location.longitude": lon,
                "days": min(days, 10),
            },
        )
        response.raise_for_status()
        return response.json()
