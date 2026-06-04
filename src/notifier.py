"""Send notifications via macOS desktop and Resend email."""

import os
import subprocess
from datetime import datetime


def notify_desktop(slots: list[dict]):
    """Send a macOS desktop notification summarizing new availability."""
    # Group by campground
    by_campground = {}
    for slot in slots:
        name = slot["campground_name"]
        by_campground.setdefault(name, []).append(slot)

    campground_names = ", ".join(by_campground.keys())
    body = f"{len(slots)} new site(s) at {campground_names}. Check email for details."

    # Truncate for osascript (notification body limit)
    if len(body) > 200:
        body = body[:197] + "..."

    # Escape double quotes for AppleScript
    body = body.replace('"', '\\"')

    cmd = (
        f'display notification "{body}" '
        f'with title "🏕 Campsite Alert" '
        f'sound name "Glass"'
    )
    subprocess.run(["osascript", "-e", cmd], capture_output=True)


def notify_email(slots: list[dict], to_address: str):
    """Send an email via Resend with availability details."""
    import resend

    resend.api_key = os.environ["RESEND_API_KEY"]

    body = _format_email_body(slots)
    subject = f"🏕 {len(slots)} new campsite(s) available!"

    resend.Emails.send({
        "from": "Campsite Finder <onboarding@resend.dev>",
        "to": [to_address],
        "subject": subject,
        "text": body,
    })


def _format_email_body(slots: list[dict]) -> str:
    """Format slots into a readable email body grouped by campground."""
    # Group by campground
    by_campground = {}
    for slot in slots:
        name = slot["campground_name"]
        cg_id = slot["campground_id"]
        by_campground.setdefault((name, cg_id), []).append(slot)

    lines = ["New campsites available!\n"]

    for (name, cg_id), cg_slots in sorted(by_campground.items()):
        lines.append(f"{name}:")
        for slot in sorted(cg_slots, key=lambda s: s["date"]):
            date = datetime.strptime(slot["date"], "%Y-%m-%d")
            date_str = date.strftime("%a %b %-d, %Y")
            site_name = slot["site_name"]
            loop = slot.get("loop", "")
            loop_str = f" ({loop})" if loop else ""
            lines.append(f"  Site {site_name}{loop_str} — {date_str}")
        lines.append(f"  Book: https://www.recreation.gov/camping/campgrounds/{cg_id}")
        lines.append("")

    lines.append("— Campsite Finder")
    return "\n".join(lines)
