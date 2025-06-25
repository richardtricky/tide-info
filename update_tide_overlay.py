import os
import requests
from datetime import datetime
from collections import defaultdict

API_KEY = os.environ.get("UKHO_API_KEY")
STATION_ID = "0513"  # Barry Dock
DAYS = 7

BASE_URL = f"https://admiraltyapi.azure-api.net/uktidalapi/api/V1/Stations/{STATION_ID}/TidalEvents"
HEADERS = {"Ocp-Apim-Subscription-Key": API_KEY}

def fetch_tide_data(days):
    params = {"duration": days}
    resp = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()  # Expect JSON array of events

def parse_datetime(dt_str):
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))

def format_tide_text(events):
    tides_by_day = defaultdict(list)
    for e in events:
        dt = parse_datetime(e["DateTime"])
        day = dt.strftime("%d-%m-%Y (%a)")
        tide_type = "High" if e["EventType"] == "HighWater" else "Low"
        time_str = dt.strftime("%H:%M")
        tides_by_day[day].append(f"{tide_type} at {time_str}")

    lines = []
    for day in sorted(tides_by_day.keys(), key=lambda d: datetime.strptime(d.split(" (")[0], "%d-%m-%Y")):
        lines.append(f"{day}: {' | '.join(tides_by_day[day])}")
    return "\n".join(lines)

def main():
    try:
        events = fetch_tide_data(DAYS)
        text = format_tide_text(events)
        print(f"Writing tides:\n{text}")
        with open("tide.txt", "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
