import os
import requests
from datetime import datetime, timezone
from collections import defaultdict

API_KEY = os.environ.get("UK_TIDE_API_KEY")
STATION_ID = "0513"  # Barry Dock station ID
DAYS = 7

BASE_URL = f"https://api.tidesapi.com/stations/{STATION_ID}/extremes"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def fetch_tide_data(days):
    params = {
        "days": days,
        "datum": "CD",
        "timezone": "Europe/London",
    }
    resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()

def parse_datetime(dt_str):
    """ Parse UTC timestamp returned by the API. Adjusts to timezone if needed. """
    # Assume the API returns ISO 8601 in UTC; we’ll localize to Europe/London if desired
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    return dt

def format_tide_text(data):
    # Group tide data by day
    tides_by_day = defaultdict(list)
    for extreme in data.get("extremes", []):
        dt = parse_datetime(extreme["datetime"])
        day = dt.strftime("%d-%m-%Y (%a)")
        tide_type = extreme["type"].title()  # "High" or "Low"
        time_str = dt.strftime("%H:%M")
        tides_by_day[day].append(f"{tide_type} at {time_str}")

    # Build output, sorted by day
    output_lines = []
    for day in sorted(
        tides_by_day.keys(),
        key=lambda d: datetime.strptime(d.split(' (')[0], "%d-%m-%Y")
    ):
        tide_info = " | ".join(tides_by_day[day])
        output_lines.append(f"{day}: {tide_info}")

    return "\n".join(output_lines)

def main():
    try:
        data = fetch_tide_data(DAYS)
        tide_text = format_tide_text(data)
        print(f"Writing tide data:\n{tide_text}")
        with open("tide.txt", "w", encoding="utf-8") as f:
            f.write(tide_text)
    except Exception as e:
        print(f"Error fetching or writing tide data: {e}")

if __name__ == "__main__":
    main()
