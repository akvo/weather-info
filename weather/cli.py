"""Command-line interface for weather tool."""

import argparse
import sys

from weather.services import (
    OpenWeatherMapService,
    WeatherAPIService,
    GoogleWeatherService,
)
from weather.formatters import (
    format_json,
    format_text,
    format_raw_json,
    format_raw_text,
)


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="weather",
        description="Fetch weather data from multiple providers",
    )
    parser.add_argument(
        "--service",
        choices=["owm", "wa", "gw"],
        required=True,
        help="Weather service: owm (OpenWeatherMap), wa (WeatherAPI), gw (Google)",
    )
    parser.add_argument(
        "--location",
        help="Location to get weather for (e.g., 'Jakarta', 'London,UK')",
    )
    parser.add_argument(
        "--lat",
        type=float,
        help="Latitude (use with --lon instead of --location)",
    )
    parser.add_argument(
        "--lon",
        type=float,
        help="Longitude (use with --lat instead of --location)",
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
        help="Forecast type: hour (hourly) or day (daily). Omit for current.",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Show raw API response without mapping",
    )
    return parser


def validate_location_args(args) -> tuple[bool, str | None]:
    """Validate location arguments.

    Returns:
        Tuple of (use_coords: bool, error_message: str | None)
    """
    has_location = args.location is not None
    has_lat = args.lat is not None
    has_lon = args.lon is not None

    if has_location and (has_lat or has_lon):
        return False, "Cannot use --location with --lat/--lon. Use one or the other."

    if has_lat and not has_lon:
        return False, "--lat requires --lon"

    if has_lon and not has_lat:
        return False, "--lon requires --lat"

    if not has_location and not (has_lat and has_lon):
        return False, "Must provide either --location or --lat and --lon"

    return (has_lat and has_lon), None


def get_service(service_name: str):
    """Get weather service instance."""
    if service_name == "owm":
        return OpenWeatherMapService()
    elif service_name == "wa":
        return WeatherAPIService()
    elif service_name == "gw":
        return GoogleWeatherService()
    raise ValueError(f"Unknown service: {service_name}")


def main(args: list[str] | None = None) -> int:
    """Main entry point."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Validate location arguments
    use_coords, error = validate_location_args(parsed_args)
    if error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    try:
        service = get_service(parsed_args.service)

        if parsed_args.raw:
            # Get raw API response
            if use_coords:
                if parsed_args.forecast:
                    data = service.get_forecast_raw_by_coords(
                        parsed_args.lat, parsed_args.lon
                    )
                else:
                    data = service.get_current_raw_by_coords(
                        parsed_args.lat, parsed_args.lon
                    )
            else:
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
            if use_coords:
                if parsed_args.forecast == "hour":
                    data = service.get_forecast_hourly_by_coords(
                        parsed_args.lat, parsed_args.lon
                    )
                elif parsed_args.forecast == "day":
                    data = service.get_forecast_daily_by_coords(
                        parsed_args.lat, parsed_args.lon
                    )
                else:
                    data = service.get_current_by_coords(
                        parsed_args.lat, parsed_args.lon
                    )
            else:
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
