import requests
from datetime import datetime, timezone

API_KEY = "212ed417-7d00-412b-92f9-2d52852436b5"
LAT = 51.3932
LON = -3.2710

def fetch_tide_data(api_key, lat, lon):
    url = f"https://www.worldtides.info/api/v3?extremes&lat={lat}&lon={lon}&key={api_key}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()

def parse_iso(date_string):
    """Handle dates ending with Z"""
    if date_string.endswith("Z"):
        date_string = date_string.replace("Z", "+00:00")
    return datetime.fromisoformat(date_string)

def format_tide_text(data):
    now = datetime.now(timezone.utc)
    upcoming = [
        e for e in data.get("extremes", [])
        if parse_iso(e["date"]) > now
    ][:2]

    if not upcoming:
        return "No upcoming tide data."

    return " | ".join([
        f"{e['type']} Tide: {parse_iso(e['date']).strftime('%H:%M')}"
        for e in upcoming
    ])

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
