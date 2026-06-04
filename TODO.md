# Next Steps: Multi-User Support

## 1. Interactive onboarding (`--setup`)
CLI flow that collects email, campgrounds, dates, and check frequency, then writes `config.yaml`. No YAML editing required.

## 2. Campground search
Hit the Recreation.gov search API so users can find campgrounds by name instead of looking up IDs manually.

## 3. Flexible date input
Support ranges (`2026-07-01:2026-07-15`) and day-of-week filters (`--fridays --saturdays in july`) in addition to explicit date lists.

## 4. Resend domain verification
Register and verify a sending domain in Resend so emails can go to any recipient, not just the account owner. Required before anyone else can use the email notifications.

## 5. Example config + README
Ship `config.example.yaml` with placeholders, add `config.yaml` to `.gitignore`, and write a README with install/setup/run instructions.

## 6. Cross-platform notifications
Desktop notifications currently use macOS `osascript`. Add `notify-send` for Linux, or gracefully skip on unsupported platforms.
