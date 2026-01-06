# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install for development
pip install -e .

# Run CLI
python -m weather --service=owm --location="Jakarta"
python -m weather --service=wa --location="London" --output=json

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

Current implementations: `OpenWeatherMapService`, `WeatherAPIService`

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
