import os
import requests
from datetime import datetime, timezone

API_KEY = os.environ.get("STORMGLASS_API_KEY")  # from GitHub secret
LAT = 51.3932
LON = -3.2710

def fetch_tide_data(api_key, lat, lon):
    url = f"https://api.stormglass.io/v2/tide/extremes/point?lat={lat}&lng={lon}"
    resp = requests.get(
        url,
        headers={"Authorization": api_key},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()

def format_tide_text(data):
    now = datetime.now(timezone.utc)
    upcoming = [
        e for e in data.get("data", [])
        if datetime.fromisoformat(e["time"].replace("Z", "+00:00")) > now
    ][:2]

    if not upcoming:
        return "No upcoming tide data."

    return " | ".join(
        f"{e['type'].title()} Tide: {datetime.fromisoformat(e['time'].replace('Z', '+00:00')).strftime('%H:%M')}"
        for e in upcoming
    )

def main():
    try:
        data = fetch_tide_data(API_KEY, LAT, LON)
        text = format_tide_text(data)
        print(f"Updating tide.txt with: {text}")
        with open("tide.txt", "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        print(f"Error fetching or writing tide data: {e}")

if __name__ == "__main__":
    main()
