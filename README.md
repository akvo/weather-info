# akvo-weather-info

A Python library to fetch weather data from multiple providers (OpenWeatherMap, WeatherAPI.com).

## Installation

```bash
pip install akvo-weather-info
```

For development:
```bash
pip install -e .
```

## Configuration

Create a `.env` file in your project root with API keys:

```
OPENWEATHER=your_openweathermap_api_key
WEATHERAPI=your_weatherapi_api_key
```

Get API keys from:
- OpenWeatherMap: https://openweathermap.org/api
- WeatherAPI: https://www.weatherapi.com/

## Library Usage

### Basic Import

```python
from weather.services import OpenWeatherMapService, WeatherAPIService

# Using OpenWeatherMap
owm = OpenWeatherMapService()
current = owm.get_current("Jakarta")
print(f"Temperature: {current.temperature}C")
print(f"Condition: {current.description}")

# Using WeatherAPI.com
wa = WeatherAPIService()
current = wa.get_current("London")
print(f"Temperature: {current.temperature}C")
```

### Get Forecast

```python
from weather.services import OpenWeatherMapService

service = OpenWeatherMapService()

# Hourly forecast
hourly = service.get_forecast_hourly("Tokyo", hours=24)
for forecast in hourly:
    print(f"{forecast.forecast_time}: {forecast.temperature}C")

# Daily forecast
daily = service.get_forecast_daily("New York", days=5)
for forecast in daily:
    print(f"{forecast.forecast_time.date()}: {forecast.temperature}C")
```

### Get Raw API Response

```python
from weather.services import WeatherAPIService

service = WeatherAPIService()

# Raw response as dict
raw = service.get_current_raw("Jakarta")
print(raw["current"]["temp_c"])
print(raw["current"]["condition"]["text"])

# Raw forecast
raw_forecast = service.get_forecast_raw("Jakarta")
print(raw_forecast["forecast"]["forecastday"])
```

### Data Models

```python
from weather.models import WeatherData, Forecast

# WeatherData fields
weather.location      # str: "Jakarta, ID"
weather.temperature   # float: temperature in Celsius
weather.feels_like    # float: feels like temperature
weather.humidity      # int: humidity percentage
weather.description   # str: weather description
weather.wind_speed    # float: wind speed in m/s
weather.timestamp     # datetime: data timestamp

# Convert to dict
data_dict = weather.to_dict()
```

### Formatters

```python
from weather.services import OpenWeatherMapService
from weather.formatters import format_json, format_text

service = OpenWeatherMapService()
current = service.get_current("Jakarta")

# Format as JSON string
json_output = format_json(current)

# Format as readable text
text_output = format_text(current)
```

## CLI Usage

```bash
python -m weather --service=<SERVICE> --location=<LOCATION> [--output=<FORMAT>] [--forecast=<TYPE>] [--raw]
```

### Arguments

| Argument | Required | Values | Description |
|----------|----------|--------|-------------|
| `--service` | Yes | `owm`, `wa` | Weather service (`owm` = OpenWeatherMap, `wa` = WeatherAPI.com) |
| `--location` | Yes | string | Location name (e.g., "Jakarta", "London,UK") |
| `--output` | No | `text`, `json` | Output format (default: `text`) |
| `--forecast` | No | `hour`, `day` | Forecast type. If omitted, shows current weather |
| `--raw` | No | flag | Show raw API response without field mapping |

### CLI Examples

```bash
# Current weather
python -m weather --service=owm --location="Jakarta"

# JSON output
python -m weather --service=wa --location="London" --output=json

# Hourly forecast
python -m weather --service=wa --location="Tokyo" --forecast=hour

# Daily forecast
python -m weather --service=owm --location="New York" --forecast=day

# Raw API response
python -m weather --service=owm --location="Jakarta" --raw --output=json
```

## Project Structure

```
weather/
├── __init__.py
├── __main__.py          # CLI entry point
├── cli.py               # Argument parsing
├── config.py            # API key management
├── models.py            # Data models (WeatherData, Forecast)
├── services/
│   ├── base.py          # Abstract base class
│   ├── openweathermap.py
│   └── weatherapi.py
└── formatters/
    ├── json_formatter.py
    ├── text_formatter.py
    └── raw_formatter.py
```

## Requirements

- Python >= 3.10
- httpx
- python-dotenv
