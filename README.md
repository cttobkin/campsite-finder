# Campsite Finder

Checks Recreation.gov for campsite availability and notifies you via desktop notification and email when a site opens up.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Set your [Resend](https://resend.com) API key:

```bash
export RESEND_API_KEY=re_your_key_here
```

## Configure

Edit `config.yaml` with your campgrounds, dates, and email. Campground IDs are the numbers in Recreation.gov URLs (e.g. `recreation.gov/camping/campgrounds/232493`).

## Run

```bash
# One-shot check
python -m src.main --once

# Hourly checks
python -m src.main
```
