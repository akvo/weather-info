# akvo-weather-info

A Python library to fetch weather data from multiple providers (OpenWeatherMap, WeatherAPI.com, Google Weather).

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
GOOGLEWEATHER=your_google_maps_api_key
```

Get API keys from:
- OpenWeatherMap: https://openweathermap.org/api
- WeatherAPI: https://www.weatherapi.com/
- Google Maps Platform: https://developers.google.com/maps/documentation/weather

## Library Usage

### Basic Import

```python
from weather.services import OpenWeatherMapService, WeatherAPIService, GoogleWeatherService

# Using OpenWeatherMap
owm = OpenWeatherMapService()
current = owm.get_current("Jakarta")
print(f"Temperature: {current.temperature}C")
print(f"Condition: {current.description}")

# Using WeatherAPI.com
wa = WeatherAPIService()
current = wa.get_current("London")
print(f"Temperature: {current.temperature}C")

# Using Google Weather
gw = GoogleWeatherService()
current = gw.get_current("Tokyo")
print(f"Temperature: {current.temperature}C")
```

### Query by Coordinates

All services support coordinate-based queries:

```python
from weather.services import OpenWeatherMapService, GoogleWeatherService

# OpenWeatherMap by coordinates
owm = OpenWeatherMapService()
current = owm.get_current_by_coords(lat=-6.2088, lon=106.8456)
hourly = owm.get_forecast_hourly_by_coords(lat=-6.2088, lon=106.8456, hours=24)

# Google Weather by coordinates (skips geocoding)
gw = GoogleWeatherService()
current = gw.get_current_by_coords(lat=51.5074, lon=-0.1278)
daily = gw.get_forecast_daily_by_coords(lat=51.5074, lon=-0.1278, days=7)
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
# By location name
python -m weather --service=<SERVICE> --location=<LOCATION> [--output=<FORMAT>] [--forecast=<TYPE>] [--raw]

# By coordinates
python -m weather --service=<SERVICE> --lat=<LAT> --lon=<LON> [--output=<FORMAT>] [--forecast=<TYPE>] [--raw]
```

### Arguments

| Argument | Required | Values | Description |
|----------|----------|--------|-------------|
| `--service` | Yes | `owm`, `wa`, `gw` | Weather service (`owm` = OpenWeatherMap, `wa` = WeatherAPI.com, `gw` = Google Weather) |
| `--location` | * | string | Location name (e.g., "Jakarta", "London,UK") |
| `--lat` | * | float | Latitude (use with `--lon`) |
| `--lon` | * | float | Longitude (use with `--lat`) |
| `--output` | No | `text`, `json` | Output format (default: `text`) |
| `--forecast` | No | `hour`, `day` | Forecast type. If omitted, shows current weather |
| `--raw` | No | flag | Show raw API response without field mapping |

\* Either `--location` OR both `--lat` and `--lon` are required.

### CLI Examples

```bash
# Current weather by location
python -m weather --service=owm --location="Jakarta"

# Current weather by coordinates
python -m weather --service=gw --lat=-6.2088 --lon=106.8456

# JSON output
python -m weather --service=wa --location="London" --output=json

# Hourly forecast
python -m weather --service=gw --location="Tokyo" --forecast=hour

# Daily forecast by coordinates
python -m weather --service=owm --lat=40.7128 --lon=-74.0060 --forecast=day

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
│   ├── weatherapi.py
│   └── google_weather.py
└── formatters/
    ├── json_formatter.py
    ├── text_formatter.py
    └── raw_formatter.py
```

## Requirements

- Python >= 3.10
- httpx
- python-dotenv
