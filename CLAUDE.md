# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install for development
pip install -e .

# Run CLI (by location name)
python -m weather --service=owm --location="Jakarta"
python -m weather --service=wa --location="London" --output=json
python -m weather --service=gw --location="Tokyo" --forecast=hour

# Run CLI (by coordinates)
python -m weather --service=owm --lat=-6.2088 --lon=106.8456
python -m weather --service=gw --lat=51.5074 --lon=-0.1278 --forecast=day

# Test with raw API response
python -m weather --service=owm --location="Jakarta" --raw

# Build package
python -m build

# Upload to PyPI (via GitHub Actions on tag push)
git tag v0.1.x && git push origin v0.1.x
```

## Architecture

This is a multi-provider weather library with CLI support. Package name on PyPI is `akvo-weather-info`, import name is `weather`.

### Service Pattern
All weather providers extend `WeatherService` (abstract base class in `services/base.py`):
- `get_current(location)` → `WeatherData`
- `get_forecast_hourly(location, hours)` → `list[Forecast]`
- `get_forecast_daily(location, days)` → `list[Forecast]`
- `get_current_raw(location)` → `dict` (raw API response)
- `get_forecast_raw(location)` → `dict`

Current implementations: `OpenWeatherMapService`, `WeatherAPIService`, `GoogleWeatherService`

### OpenWeatherMap API Versions

`OpenWeatherMapService` supports both API 2.5 (default) and OneCall API 3.0:

```python
# API 2.5 (default) - location-based queries
service = OpenWeatherMapService()
data = service.get_forecast_raw("Nairobi, Kenya")

# OneCall API 3.0 - coordinate-based queries
service = OpenWeatherMapService(api_version="3.0")
data = service.get_onecall_raw(
    lat=-1.2921,
    lon=36.8219,
    exclude=["minutely", "hourly", "daily", "alerts"]  # Optional
)
```

**OneCall 3.0 exclude options:** `current`, `minutely`, `hourly`, `daily`, `alerts`

**Coordinate-based queries (API 2.5):**
```python
service = OpenWeatherMapService()
data = service.get_current_by_coords(lat=-6.2088, lon=106.8456)
hourly = service.get_forecast_hourly_by_coords(lat=51.5074, lon=-0.1278, hours=24)
daily = service.get_forecast_daily_by_coords(lat=35.6762, lon=139.6503, days=5)
raw = service.get_current_raw_by_coords(lat=-6.2088, lon=106.8456)
```

### WeatherAPI.com

`WeatherAPIService` supports both location strings and coordinates:

```python
service = WeatherAPIService()

# Location-based queries
data = service.get_current("Jakarta, Indonesia")

# Coordinate-based queries
data = service.get_current_by_coords(lat=-6.2088, lon=106.8456)
hourly = service.get_forecast_hourly_by_coords(lat=51.5074, lon=-0.1278, hours=24)
daily = service.get_forecast_daily_by_coords(lat=35.6762, lon=139.6503, days=3)
raw = service.get_current_raw_by_coords(lat=-6.2088, lon=106.8456)
```

**API Limits:** Free tier limited to 3-day forecast.

### Google Maps Weather API

`GoogleWeatherService` uses the Google Maps Platform Weather API:

```python
service = GoogleWeatherService()

# Location-based queries (geocoded automatically)
data = service.get_current("Jakarta, Indonesia")
hourly = service.get_forecast_hourly("London, UK", hours=24)
daily = service.get_forecast_daily("New York", days=7)

# Coordinate-based queries (no geocoding)
data = service.get_current_by_coords(lat=-6.2088, lon=106.8456)
hourly = service.get_forecast_hourly_by_coords(lat=51.5074, lon=-0.1278, hours=24)
daily = service.get_forecast_daily_by_coords(lat=35.6762, lon=139.6503, days=7)

# Raw API responses
raw_current = service.get_current_raw("Tokyo")
raw_daily = service.get_daily_forecast_raw("Paris", days=10)

# Raw by coordinates
raw = service.get_current_raw_by_coords(lat=-6.2088, lon=106.8456)
raw_hourly = service.get_forecast_raw_by_coords(lat=51.5074, lon=-0.1278, hours=48)
raw_daily = service.get_daily_forecast_raw_by_coords(lat=35.6762, lon=139.6503, days=10)
```

**API Limits:** Hourly forecast up to 240 hours, daily forecast up to 10 days.

### Data Flow
```
CLI (cli.py) → Service → API → WeatherData/Forecast models → Formatter → Output
```

### Adding a New Weather Provider
1. Create `services/newprovider.py` extending `WeatherService`
2. Add API key getter in `config.py`
3. Export in `services/__init__.py`
4. Add service option in `cli.py` (`get_service()` function)

## Configuration

API keys loaded from `.env` file via python-dotenv:
- `OPENWEATHER` - OpenWeatherMap API key
- `WEATHERAPI` - WeatherAPI.com API key
- `GOOGLEWEATHER` - Google Maps Platform API key (for Weather API)
