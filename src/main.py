"""Campsite availability checker — entry point."""

import sys
import time
import traceback

import schedule
from dotenv import load_dotenv

from src.checker import run_check
from src.config import load_config

# Load secrets (e.g. RESEND_API_KEY) from a local .env so the checker can run
# unattended without sourcing the user's shell profile.
load_dotenv()


def safe_run_check(config: dict):
    """Wrapper that catches all exceptions so the scheduler never dies."""
    try:
        run_check(config)
    except Exception:
        traceback.print_exc()
        print("  [!] Check cycle failed. Will retry next interval.\n")


def main():
    config = load_config()

    campground_names = ", ".join(cg["name"] for cg in config["campgrounds"])
    print(f"Campsite Finder started.")
    print(f"  Campgrounds: {campground_names}")
    print(f"  Dates: {', '.join(sorted(config['_dates_set']))}")
    print(f"  Checking every {config['check_interval_minutes']} minutes")
    print()

    # Run immediately on startup
    safe_run_check(config)

    # If --once flag, exit after the first check
    if "--once" in sys.argv:
        return

    # Schedule recurring checks
    interval = config["check_interval_minutes"]
    schedule.every(interval).minutes.do(safe_run_check, config)

    print(f"\nScheduler running. Next check in {interval} minutes. Ctrl+C to stop.\n")

    try:
        while True:
            schedule.run_pending()
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
