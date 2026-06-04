"""Persist already-notified slots to avoid duplicate notifications."""

import json
from datetime import datetime, timezone
from pathlib import Path

SEEN_PATH = Path(__file__).parent.parent / "data" / "seen.json"


def load_seen() -> set[str]:
    """Load the set of already-notified slot keys."""
    if not SEEN_PATH.exists():
        return set()

    try:
        with open(SEEN_PATH) as f:
            data = json.load(f)
        return set(data.get("keys", []))
    except (json.JSONDecodeError, KeyError, TypeError):
        print(f"  [!] Corrupted {SEEN_PATH}, starting fresh.")
        return set()


def save_seen(seen: set[str]):
    """Write the seen set back to disk."""
    SEEN_PATH.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "keys": sorted(seen),
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }

    with open(SEEN_PATH, "w") as f:
        json.dump(data, f, indent=2)
