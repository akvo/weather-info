"""Raw output formatter - displays all fields from API response."""

import json


def format_raw_json(data: dict) -> str:
    """Format raw data as JSON."""
    return json.dumps(data, indent=2)


def format_raw_text(data: dict, indent: int = 0) -> str:
    """Format raw data as text with key-value pairs."""
    lines = []
    prefix = "  " * indent

    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(format_raw_text(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{prefix}{key}:")
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    lines.append(f"{prefix}  [{i}]:")
                    lines.append(format_raw_text(item, indent + 2))
                else:
                    lines.append(f"{prefix}  [{i}]: {item}")
        else:
            lines.append(f"{prefix}{key}: {value}")

    return "\n".join(lines)
