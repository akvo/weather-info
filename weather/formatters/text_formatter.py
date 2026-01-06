"""Text output formatter."""

from weather.models import WeatherData, Forecast


def format_text(data: WeatherData | list[Forecast]) -> str:
    """Format weather data as human-readable text."""
    if isinstance(data, list):
        return _format_forecast_list(data)
    return _format_current(data)


def _format_current(data: WeatherData) -> str:
    """Format current weather data."""
    lines = [
        f"Location: {data.location}",
        f"Temperature: {data.temperature:.1f}C (feels like {data.feels_like:.1f}C)",
        f"Humidity: {data.humidity}%",
        f"Condition: {data.description}",
        f"Wind: {data.wind_speed:.1f} m/s",
        f"Updated: {data.timestamp.strftime('%Y-%m-%d %H:%M')}",
    ]
    return "\n".join(lines)


def _format_forecast_list(forecasts: list[Forecast]) -> str:
    """Format forecast list."""
    if not forecasts:
        return "No forecast data available."

    lines = [f"Location: {forecasts[0].location}", ""]
    for forecast in forecasts:
        time_str = forecast.forecast_time.strftime("%Y-%m-%d %H:%M") if forecast.forecast_time else "N/A"
        lines.append(
            f"  {time_str}: {forecast.temperature:.1f}C, {forecast.description}, "
            f"Humidity: {forecast.humidity}%, Wind: {forecast.wind_speed:.1f} m/s"
        )
    return "\n".join(lines)
