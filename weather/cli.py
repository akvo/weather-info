"""Command-line interface for weather tool."""

import argparse
import sys

from weather.services import OpenWeatherMapService, WeatherAPIService
from weather.formatters import format_json, format_text, format_raw_json, format_raw_text


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="weather",
        description="Fetch weather data from multiple providers",
    )
    parser.add_argument(
        "--service",
        choices=["owm", "wa"],
        required=True,
        help="Weather service: owm (OpenWeatherMap) or wa (WeatherAPI.com)",
    )
    parser.add_argument(
        "--location",
        required=True,
        help="Location to get weather for (e.g., 'Jakarta', 'London,UK')",
    )
    parser.add_argument(
        "--output",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--forecast",
        choices=["hour", "day"],
        help="Forecast type: hour (hourly) or day (daily). If omitted, shows current weather.",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Show raw API response without mapping",
    )
    return parser


def get_service(service_name: str):
    """Get weather service instance."""
    if service_name == "owm":
        return OpenWeatherMapService()
    elif service_name == "wa":
        return WeatherAPIService()
    raise ValueError(f"Unknown service: {service_name}")


def main(args: list[str] | None = None) -> int:
    """Main entry point."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    try:
        service = get_service(parsed_args.service)

        if parsed_args.raw:
            # Get raw API response
            if parsed_args.forecast:
                data = service.get_forecast_raw(parsed_args.location)
            else:
                data = service.get_current_raw(parsed_args.location)

            if parsed_args.output == "json":
                output = format_raw_json(data)
            else:
                output = format_raw_text(data)
        else:
            # Get mapped data
            if parsed_args.forecast == "hour":
                data = service.get_forecast_hourly(parsed_args.location)
            elif parsed_args.forecast == "day":
                data = service.get_forecast_daily(parsed_args.location)
            else:
                data = service.get_current(parsed_args.location)

            if parsed_args.output == "json":
                output = format_json(data)
            else:
                output = format_text(data)

        print(output)
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
