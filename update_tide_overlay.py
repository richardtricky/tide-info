import os
import requests
from datetime import datetime
from collections import defaultdict

# Configuration
API_KEY = os.environ.get("UKHO_API_KEY")
STATION_ID = "0513"  # Barry Dock
DAYS = 7

BASE_URL = f"https://admiraltyapi.azure-api.net/uktidalapi/api/V1/Stations/{STATION_ID}/TidalEvents"
HEADERS = {"Ocp-Apim-Subscription-Key": API_KEY}


def fetch_tide_data(days: int):
    """Fetch tide data for the next `days` days for the station."""
    print(f"DEBUG: Using API key: {API_KEY}")
    params = {"duration": days}
    resp = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
    resp.raise_for_status()  # Will raise HTTPError if status != 200
    return resp.json()  # List of tide event dicts


def parse_datetime(dt_str: str) -> datetime:
    """Convert API's ISO string to Python datetime (UTC)."""
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))


def format_tide_text(events: list) -> str:
    """Group tide events by day and format into a string."""
    tides_by_day = defaultdict(list)

    for event in events:
        dt = parse_datetime(event["DateTime"])
        day_label = dt.strftime("%d-%m-%Y (%a)")
        tide_type = "High" if event["EventType"] == "HighWater" else "Low"
        tides_by_day[day_label].append(f"{tide_type} at {dt.strftime('%H:%M')}")

    # Sort by date
    sorted_days = sorted(
        tides_by_day.keys(),
        key=lambda d: datetime.strptime(d.split(" (")[0], "%d-%m-%Y"),
    )

    # Build output
    output_lines = []
    for day in sorted_days:
        output_lines.append(f"{day}: {' | '.join(tides_by_day[day])}")

    return "\n".join(output_lines)


def main():
    if not API_KEY:
        print("Error: UKHO_API_KEY is not set in environment variables!")
        return

    try:
        events = fetch_tide_data(DAYS)
        tide_text = format_tide_text(events)
        print("Writing tide times:\n" + tide_text)

        with open("tide.txt", "w", encoding="utf-8") as f:
            f.write(tide_text)

    except requests.HTTPError as http_err:
        print(f"Error: HTTP request failed ({http_err.response.status_code}): {http_err}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
