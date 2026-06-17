"""Fetch campsite availability, filter, diff, and notify."""

import time
from datetime import datetime, timezone

import requests

from src.notifier import notify_desktop, notify_email
from src.store import load_seen, save_seen

API_BASE = "https://www.recreation.gov/api/camps/availability/campground/{cg_id}/month"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
}

# Delay between API requests (seconds) — be respectful
REQUEST_DELAY = 0.5


def run_check(config: dict):
    """Run one full check cycle: fetch → filter → diff → notify."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Step 1: Fetch availability for all campground × month combos
    all_slots = []
    for campground in config["campgrounds"]:
        for month in config["_months"]:
            slots = _fetch_and_filter(campground, month, config["_dates_set"])
            all_slots.extend(slots)
            time.sleep(REQUEST_DELAY)

    # Step 2: Diff against seen set
    seen = load_seen()
    new_slots = []
    for slot in all_slots:
        key = f"{slot['campground_id']}:{slot['site_id']}:{slot['date']}"
        if key not in seen:
            new_slots.append(slot)
            seen.add(key)

    # Step 3: Persist updated seen set
    if new_slots:
        save_seen(seen)

    # Step 4: Notify — trigger on new slots, but include ALL available in the message
    if new_slots:
        new_keys = {
            f"{s['campground_id']}:{s['site_id']}:{s['date']}" for s in new_slots
        }
        notif = config["notifications"]

        if notif.get("desktop"):
            try:
                notify_desktop(all_slots, new_count=len(new_slots))
            except Exception as e:
                print(f"  [!] Desktop notification failed: {e}")

        email_config = notif.get("email", {})
        if email_config.get("enabled"):
            try:
                notify_email(all_slots, email_config["to"], new_keys=new_keys)
            except Exception as e:
                print(f"  [!] Email notification failed: {e}")

    # Step 5: Log
    print(
        f"[{now}] Check complete. "
        f"{len(all_slots)} available, {len(new_slots)} new."
        + (" Notified." if new_slots else "")
    )


def _fetch_and_filter(
    campground: dict, month: str, dates_set: set[str]
) -> list[dict]:
    """Fetch availability for one campground/month and filter to matching dates."""
    cg_id = campground["id"]
    cg_name = campground["name"]
    url = API_BASE.format(cg_id=cg_id)
    params = {"start_date": f"{month}-01T00:00:00.000Z"}

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as e:
        print(f"  [!] Failed to fetch {cg_name} ({month}): {e}")
        return []

    campsites = data.get("campsites") or {}
    exclude_loops = set(campground.get("exclude_loops", []))
    slots = []

    for site_id, site_info in campsites.items():
        if not isinstance(site_info, dict):
            continue

        site_name = site_info.get("site", "?")
        loop = site_info.get("loop", "")

        if loop in exclude_loops:
            continue

        availabilities = site_info.get("availabilities") or {}

        for date_str, status in availabilities.items():
            if status != "Available":
                continue

            # Parse the ISO date to YYYY-MM-DD for comparison
            date_key = date_str[:10]  # "2026-06-12T00:00:00Z" → "2026-06-12"

            if date_key not in dates_set:
                continue

            slots.append({
                "campground_id": cg_id,
                "campground_name": cg_name,
                "site_id": site_id,
                "site_name": site_name,
                "loop": loop,
                "date": date_key,
            })

    return slots
