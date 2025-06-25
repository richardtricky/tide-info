import os
import requests
from datetime import datetime, timezone
from collections import defaultdict

API_KEY = os.environ.get("TIDE_API_KEY")
LAT = 51.5045
LON = -2.7062

def fetch_tide_data(api_key, lat, lon):
    # Request up to 7 days of extremes
    url = f"https://www.worldtides.info/api/v3?extremes&days=7&lat={lat}&lon={lon}&key={api_key}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()

def parse_iso(date_string):
    if date_string.endswith("Z"):
        date_string = date_string.replace("Z", "+00:00")
    return datetime.fromisoformat(date_string)

def format_tide_text(data):
    now = datetime.now(timezone.utc)
    upcoming = [
        e for e in data.get("extremes", [])
        if parse_iso(e["date"]) > now
    ]

    if not upcoming:
        return "No upcoming tide data."

    tides_by_day = defaultdict(list)
    for e in upcoming:
        day_str = parse_iso(e['date']).strftime("%d-%m-%Y (%a)")
        tides_by_day[day_str].append(
            f"{e['type']} Tide at {parse_iso(e['date']).strftime('%H:%M')}"
        )

    # Sort the days chronologically
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
        data = fetch_tide_data(API_KEY, LAT, LON)
        text = format_tide_text(data)
        print(f"Updating tide.txt with:\n{text}")
        with open("tide.txt", "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        print(f"Error fetching or writing tide data: {e}")

if __name__ == "__main__":
    main()
