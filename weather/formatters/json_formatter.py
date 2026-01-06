"""JSON output formatter."""

import json

from weather.models import WeatherData, Forecast


def format_json(data: WeatherData | list[Forecast]) -> str:
    """Format weather data as JSON."""
    if isinstance(data, list):
        return json.dumps([item.to_dict() for item in data], indent=2)
    return json.dumps(data.to_dict(), indent=2)
