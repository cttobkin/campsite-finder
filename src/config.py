"""Parse and validate config.yaml."""

import os
from datetime import datetime
from pathlib import Path

import yaml


def load_config(path: str = None) -> dict:
    """Load config from YAML file, validate, and enrich with derived fields."""
    if path is None:
        path = Path(__file__).parent.parent / "config.yaml"

    with open(path) as f:
        config = yaml.safe_load(f)

    _validate(config)

    # Derive unique months from the dates list (for API queries)
    dates_set = set()
    months_set = set()
    for d in config["dates"]:
        parsed = datetime.strptime(d, "%Y-%m-%d")
        dates_set.add(d)
        months_set.add(parsed.strftime("%Y-%m"))

    config["_dates_set"] = dates_set
    config["_months"] = sorted(months_set)

    return config


def _validate(config: dict):
    """Validate required config fields."""
    required = ["campgrounds", "dates", "check_interval_minutes", "notifications"]
    for key in required:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

    if not config["campgrounds"]:
        raise ValueError("At least one campground is required")

    for cg in config["campgrounds"]:
        if "id" not in cg or "name" not in cg:
            raise ValueError(f"Campground must have 'id' and 'name': {cg}")

    if not config["dates"]:
        raise ValueError("At least one date is required")

    for d in config["dates"]:
        try:
            datetime.strptime(d, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format (expected YYYY-MM-DD): {d}")

    notif = config["notifications"]
    if notif.get("email", {}).get("enabled"):
        if not notif["email"].get("to"):
            raise ValueError("Email notification enabled but no 'to' address configured")
        api_key = os.environ.get("RESEND_API_KEY", "")
        if not api_key:
            raise ValueError(
                "Email notification enabled but RESEND_API_KEY environment variable is not set"
            )
